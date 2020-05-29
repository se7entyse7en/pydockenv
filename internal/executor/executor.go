package executor

import (
	"bufio"
	"context"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/docker/go-connections/nat"
	"github.com/se7entyse7en/pydockenv/internal/utils"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
)

type CommandAlias struct {
	Cmd   string
	Ports []int
}

type CommandAliases map[string]CommandAlias

func Execute(cmd []string, options *ExecOptions) error {
	logger := log.Logger
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	envName := utils.GetCurrentEnv()
	contName := fmt.Sprintf("%s_%s", utils.RESOURCES_PREFIX, envName)
	ctxLogger := logger.WithFields(logrus.Fields{
		"container-name": contName,
	})

	contInfo, err := cli.ContainerInspect(context.Background(), contName)
	if err != nil {
		return fmt.Errorf("cannot inspect container: %w", err)
	}

	if len(cmd) == 1 {
		// TODO: consider also handling len(cmd) > 1, cmd[1:] could be passed
		// as arguments to the alias
		alias, aliasExecOptions, err := lookupAlias(cmd[0], contInfo.Config.Labels["aliases"], options)
		if err == nil {
			return ExecuteForContainer(contInfo, alias, aliasExecOptions)
		}

		ctxLogger.Debugf("Failed looking up for alias: %w", err)
	}

	return ExecuteForContainer(contInfo, cmd, options)
}

func ExecuteForContainer(container types.ContainerJSON, cmd []string, options *ExecOptions) error {
	logger := log.Logger
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	hostBaseWd := container.Config.Labels["workdir"]
	wd, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("cannot get working directory: %w", err)
	}

	if !strings.HasPrefix(wd, hostBaseWd) && !options.ByPassCheck {
		return fmt.Errorf("cannot run commands outside of %s", hostBaseWd)
	}

	relativeWd := wd[len(hostBaseWd):]
	guestWd := fmt.Sprintf("/usr/src%s", relativeWd)

	ctxLogger := logger.WithFields(logrus.Fields{
		"command": strings.Join(cmd, " "),
	})

	ctxLogger.Debug("Running command...")
	err = withPortMapper(container, options.Ports, options.Detach, func() error {
		idResp, err := cli.ContainerExecCreate(context.Background(), container.ID,
			types.ExecConfig{
				Tty:          true,
				AttachStdin:  !options.Detach,
				AttachStderr: true,
				AttachStdout: true,
				Detach:       options.Detach,
				Env:          buildEnv(options.EnvVars),
				WorkingDir:   guestWd,
				Cmd:          cmd,
			})
		if err != nil {
			return fmt.Errorf("cannot create command '%s' in container '%s': %w",
				cmd, container.ID, err)
		}

		resp, err := cli.ContainerExecAttach(context.Background(), idResp.ID, types.ExecStartCheck{})
		if err != nil {
			return fmt.Errorf("cannot execute command '%s' in container '%s': %w",
				cmd, container.ID, err)
		}

		defer resp.Close()

		inout := make(chan []byte)
		go func() {
			scanner := bufio.NewScanner(os.Stdin)
			for scanner.Scan() {
				inout <- []byte(scanner.Text())
			}

			close(inout)
		}()

		go func(w io.WriteCloser) {
			for {
				data, ok := <-inout
				if !ok {
					w.Close()
					return
				}

				w.Write(append(data, '\n'))
			}
		}(resp.Conn)

		for {
			header := make([]byte, 8)
			_, err = io.ReadFull(resp.Reader, header)
			if err != nil {
				if err == io.EOF {
					break
				}

				_, ok := <-inout
				if !ok {
					// For some reason when `inout` is closed the
					// error is not `io.EOF`, so we check if the
					// channel has been closed
					return nil
				}

				return err
			}

			size := binary.BigEndian.Uint32(header[4:])
			body := make([]byte, size)
			_, err = io.ReadFull(resp.Reader, body)
			if err != nil {
				return err
			}

			if header[0] == 1 {
				os.Stdout.Write(body)
			} else {
				os.Stderr.Write(body)
			}
		}

		return nil
	})

	if err != nil {
		return err
	}

	ctxLogger.Debug("Command ran")
	return nil
}

func buildEnv(envMapping map[string]string) []string {
	var env []string
	for k, v := range envMapping {
		env = append(env, fmt.Sprintf("%s=%s", k, v))
	}

	return env
}

func lookupAlias(cmd string, rawAliases string, options *ExecOptions) ([]string, *ExecOptions, error) {
	logger := log.Logger
	ctxLogger := logger.WithFields(logrus.Fields{"cmd": cmd})
	ctxLogger.Debug("Looking for aliases for command...")
	if rawAliases != "" {
		var parsedAliases CommandAliases
		json.Unmarshal([]byte(rawAliases), &parsedAliases)
		ctxLogger.Debugf("Found %d aliases", len(parsedAliases))
		if alias, ok := parsedAliases[cmd]; ok {
			options.Ports = []int{}
			keys := make(map[int]bool)
			for _, p := range append(options.Ports, alias.Ports...) {
				if _, value := keys[p]; !value {
					keys[p] = true
					options.Ports = append(options.Ports, p)
				}
			}

			return strings.Split(alias.Cmd, " "), options, nil
		}

		return []string{}, nil, fmt.Errorf("No alias found for command")
	}

	return []string{}, nil, fmt.Errorf("No aliases defined")
}

func withPortMapper(cj types.ContainerJSON, ports []int, detach bool, f func() error) error {
	logger := log.Logger
	ctxLogger := logger.WithFields(logrus.Fields{"ports": ports})
	ctxLogger.Debug("Running port mappers...")

	containerNames, err := runPortMapper(cj, ports)
	if err != nil {
		return fmt.Errorf("cannot run port mapper: %w", err)
	}

	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	err = f()
	if err != nil {
		return err
	}

	if detach {
		return nil
	}

	ctxLogger.Debug("Stopping port mappers...")
	for _, cName := range containerNames {
		err = cli.ContainerStop(context.Background(), cName, nil)
		if err != nil {
			return fmt.Errorf("cannot stop container: %w", err)
		}
	}

	return nil
}

func runPortMapper(cj types.ContainerJSON, ports []int) ([]string, error) {
	logger := log.Logger

	if len(ports) == 0 {
		return []string{}, nil
	}

	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return []string{}, err
	}

	netName := cj.HostConfig.NetworkMode.NetworkName()
	guestIp := cj.NetworkSettings.Networks[netName].IPAddress

	var containersNames []string
	for _, p := range ports {
		// TODO: Use a single container for all port mappings instead of
		// spinning a container for each port
		contName := fmt.Sprintf("%s_port_mapper_%d", cj.Name, p)
		ctxLogger := logger.WithFields(logrus.Fields{
			"port":           p,
			"container-name": contName,
		})
		_, err := cli.ContainerInspect(context.Background(), contName)
		if err != nil {
			cmd := fmt.Sprintf("TCP-LISTEN:1234,fork TCP-CONNECT:%s:%d",
				guestIp, p)
			guestPort := fmt.Sprintf("%d/tcp", p)

			ctxLogger := ctxLogger.WithFields(logrus.Fields{
				"cmd":        cmd,
				"guest-port": guestPort,
			})
			ctxLogger.Debug("Creating port mapper container...")
			_, err := cli.ContainerCreate(
				context.Background(),
				&container.Config{
					Image: "alpine/socat",
					Cmd:   strings.Split(cmd, " "),
					ExposedPorts: nat.PortSet{
						"1234/tcp": struct{}{},
					},
				},
				&container.HostConfig{
					AutoRemove: true,
					PortBindings: map[nat.Port][]nat.PortBinding{
						"1234/tcp": {{
							HostIP:   "0.0.0.0",
							HostPort: guestPort,
						}},
					},
					NetworkMode: container.NetworkMode(netName),
				},
				&network.NetworkingConfig{},
				contName,
			)
			if err != nil {
				return []string{}, fmt.Errorf("cannot create container: %w", err)
			}

			ctxLogger.Debug("Port mapper container created!")
		}

		ctxLogger.Debug("Running port mapper...")
		err = cli.ContainerStart(context.Background(), contName,
			types.ContainerStartOptions{})
		if err != nil {
			return []string{}, fmt.Errorf("cannot start container: %w", err)
		}

		ctxLogger.Debug("Port mapper ran!")
		containersNames = append(containersNames, contName)
	}

	return containersNames, nil
}

type ExecOptions struct {
	ByPassCheck bool
	Detach      bool
	EnvVars     map[string]string
	Ports       []int
}
