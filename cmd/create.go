package cmd

import (
	"io/ioutil"

	"github.com/pelletier/go-toml"
	"github.com/se7entyse7en/pydockenv/internal/environment"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var createCmd = &cobra.Command{
	Use:   "create [project-dir]",
	Short: "Create a virtual environment",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		cmdArgs, err := parseCreateArgs(cmd, args)
		if err != nil {
			logger.WithError(err).Fatal("Cannot parse arguments")
		}

		conf, err := parseConfig(cmdArgs)

		ctxLogger := logger.WithFields(logrus.Fields{
			"project-dir": cmdArgs.ProjectDir,
			"toml-file":   cmdArgs.TomlFile,
			"name":        conf.Name,
			"version":     conf.Python,
		})
		ctxLogger.Info("Creating virtual environment...")

		if err := environment.Create(conf); err != nil {
			logger.WithError(err).Fatal("Cannot create virtual environment")
		}

		ctxLogger.Info("Virtual environment created!")
	},
}

func parseCreateArgs(cmd *cobra.Command, args []string) (*createArgs, error) {
	projectDir := args[0]

	tomlFile, err := getStringArg(cmd, "toml-file")
	if err != nil {
		return nil, err
	}

	name, err := getStringArg(cmd, "name")
	if err != nil {
		return nil, err
	}

	version, err := getStringArg(cmd, "version")
	if err != nil {
		return nil, err
	}

	return &createArgs{
		ProjectDir: projectDir,
		TomlFile:   tomlFile,
		Name:       name,
		Version:    version,
	}, nil
}

func parseConfig(cmdArgs *createArgs) (*environment.Config, error) {
	if cmdArgs.TomlFile != "" {
		b, err := ioutil.ReadFile(cmdArgs.TomlFile)
		if err != nil {
			return nil, err
		}

		rawConfig := environment.RawConfig{}
		toml.Unmarshal(b, &rawConfig)

		conf := rawConfig.Tool.Pydockenv
		conf.ProjectDir = cmdArgs.ProjectDir
		if conf.Python == "" {
			conf.Python = "latest"
		}
		return conf, nil
	}

	python := "latest"
	if cmdArgs.Version != "" {
		python = cmdArgs.Version
	}

	return &environment.Config{
		Name:       cmdArgs.Name,
		ProjectDir: cmdArgs.ProjectDir,
		Python:     python,
	}, nil
}

type createArgs struct {
	ProjectDir string
	TomlFile   string
	Name       string
	Version    string
}

func init() {
	rootCmd.AddCommand(createCmd)

	createCmd.Flags().StringP("toml-file", "f", "", "Toml file")
	createCmd.Flags().StringP("name", "n", "", "Environment name")
	createCmd.Flags().StringP("version", "v", "", "Python version")
}
