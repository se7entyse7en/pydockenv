package environment

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/mount"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/jsonmessage"
	"github.com/docker/docker/pkg/term"
	"github.com/se7entyse7en/pydockenv/internal/utils"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
)

type Config struct {
	Name          string
	Python        string
	ProjectDir    string
	Dependencies  map[string]string
	ContainerArgs map[string]string
	Aliases       map[string]struct {
		Cmd   string
		Ports []int
	}
}

type RawConfig struct {
	Tool struct {
		Pydockenv *Config
	}
}

func Create(conf *Config) error {
	logger := log.Logger
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	contImg := fmt.Sprintf("python:%s", conf.Python)
	images, err := listDockerImages(cli)
	if err != nil {

		return fmt.Errorf("cannot list docker images: %w", err)
	}

	ctxLogger := logger.WithFields(logrus.Fields{
		"image": contImg,
	})

	if _, ok := images[contImg]; !ok {
		ctxLogger.Debug("Image not found, pulling...")
		out, err := cli.ImagePull(context.Background(), contImg,
			types.ImagePullOptions{})
		if err != nil {
			return fmt.Errorf("cannot pull image: %w", err)
		}

		defer out.Close()

		termFd, isTerm := term.GetFdInfo(os.Stderr)
		jsonmessage.DisplayJSONMessagesStream(out, os.Stderr, termFd, isTerm, nil)

		ctxLogger.Debug("Image pulled!")
	}

	netName := fmt.Sprintf("%s_%s_network", utils.RESOURCES_PREFIX, conf.Name)
	ctxLogger = logger.WithFields(logrus.Fields{
		"network-name": netName,
	})

	ctxLogger.Debug("Creating network...")
	_, err = cli.NetworkCreate(
		context.Background(),
		netName,
		types.NetworkCreate{CheckDuplicate: true},
	)
	if err != nil {
		return fmt.Errorf("cannot create network: %w", err)
	}

	ctxLogger.Debug("Network created!")

	contName := fmt.Sprintf("%s_%s", utils.RESOURCES_PREFIX, conf.Name)
	workdir, err := filepath.Abs(conf.ProjectDir)
	if err != nil {
		return err
	}

	ctxLogger = logger.WithFields(logrus.Fields{
		"container-image": contImg,
		"container-name":  contName,
		"workdir":         workdir,
	})
	ctxLogger.Debug("Creating container...")

	jsonAliases, err := json.Marshal(conf.Aliases)
	if err != nil {
		return err
	}

	_, err = cli.ContainerCreate(
		context.Background(),
		&container.Config{
			Image:     contImg,
			Cmd:       []string{"/bin/sh"},
			OpenStdin: true,
			Labels: map[string]string{
				"workdir":  workdir,
				"env_name": conf.Name,
				"aliases":  string(jsonAliases),
			},
		},
		&container.HostConfig{
			NetworkMode: container.NetworkMode(netName),
			Mounts: []mount.Mount{
				{
					Source: workdir,
					Target: "/usr/src",
					Type:   mount.TypeBind,
				},
			},
		},
		&network.NetworkingConfig{},
		contName,
	)
	if err != nil {
		return fmt.Errorf("cannot create container: %w", err)
	}

	ctxLogger.Debug("Container created!")

	return nil
}

func Status() error {
	logger := log.Logger
	envName := utils.GetCurrentEnv()
	if envName == "" {
		logger.Info("No active environment")
		return nil
	}

	logger.Infof("Active environment: %s", envName)
	return nil
}

func Activate(envName string) error {
	logger := log.Logger
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	contName := fmt.Sprintf("%s_%s", utils.RESOURCES_PREFIX, envName)

	ctxLogger := logger.WithFields(logrus.Fields{
		"container-name": contName,
	})
	ctxLogger.Debug("Starting container...")

	err = cli.ContainerStart(context.Background(), contName,
		types.ContainerStartOptions{})
	if err != nil {
		return fmt.Errorf("cannot start container: %w", err)
	}

	ctxLogger.Debug("Container started!")

	return nil
}

func Deactivate() error {
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
	ctxLogger.Debug("Stopping container...")

	err = cli.ContainerStop(context.Background(), contName, nil)
	if err != nil {
		return fmt.Errorf("cannot stop container: %w", err)
	}

	ctxLogger.Debug("Container stopped!")

	return nil
}

func ListEnvironments() error {
	logger := log.Logger

	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	currentEnvName := utils.GetCurrentEnv()
	containers, err := cli.ContainerList(
		context.Background(), types.ContainerListOptions{All: true})
	if err != nil {
		return fmt.Errorf("cannot list containers: %w", err)
	}

	var msgBuilder strings.Builder
	for _, c := range containers {
		contName := c.Names[0]
		if !strings.HasPrefix(contName, utils.RESOURCES_PREFIX) {
			continue
		}

		envName := contName[len(utils.RESOURCES_PREFIX):]
		m := fmt.Sprintf("%s\n", envName)
		if envName == currentEnvName {
			m = fmt.Sprintf("* %s", m)
		}

		msgBuilder.WriteString(m)
	}

	msg := msgBuilder.String()
	if msg == "" {
		logger.Info("No environments available")
	} else {
		logger.Info(msg)
	}

	return nil
}

func Remove(envName string) error {
	logger := log.Logger
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		return err
	}

	contName := fmt.Sprintf("%s_%s", utils.RESOURCES_PREFIX, envName)

	ctxLogger := logger.WithFields(logrus.Fields{
		"container-name": contName,
	})
	ctxLogger.Debug("Removing container...")

	err = cli.ContainerRemove(context.Background(), contName,
		types.ContainerRemoveOptions{
			RemoveVolumes: true,
			Force:         true,
		})
	if err != nil {
		return fmt.Errorf("cannot remove container: %w", err)
	}

	ctxLogger.Debug("Container removed!")

	netName := fmt.Sprintf("%s_%s_network", utils.RESOURCES_PREFIX, envName)
	ctxLogger = logger.WithFields(logrus.Fields{
		"network-name": netName,
	})

	ctxLogger.Debug("Removing network...")
	err = cli.NetworkRemove(context.Background(), netName)
	if err != nil {
		return fmt.Errorf("cannot remove network: %w", err)
	}

	ctxLogger.Debug("Network Removed!")
	return nil
}

func listDockerImages(cli *client.Client) (map[string]struct{}, error) {
	images, err := cli.ImageList(context.Background(),
		types.ImageListOptions{All: true})

	var imagesNames map[string]struct{}
	if err != nil {
		return imagesNames, err
	}

	imagesNames = make(map[string]struct{})
	for _, im := range images {
		for _, tag := range im.RepoTags {
			if tag == "<none>:<none>" {
				continue
			}

			imagesNames[tag] = struct{}{}
		}
	}

	return imagesNames, nil
}
