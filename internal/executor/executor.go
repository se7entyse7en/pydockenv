package executor

import (
	"context"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
)

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
	idResp, err := cli.ContainerExecCreate(context.Background(), container.Name,
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

	for {
		header := make([]byte, 8)
		_, err = io.ReadFull(resp.Reader, header)
		if err != nil {
			if err == io.EOF {
				break
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

type ExecOptions struct {
	ByPassCheck bool
	Detach      bool
	EnvVars     map[string]string
	Ports       []int
}
