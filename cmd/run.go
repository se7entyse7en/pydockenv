package cmd

import (
	"strconv"
	"strings"

	"github.com/se7entyse7en/pydockenv/internal/executor"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var runCmd = &cobra.Command{
	Use:   "run [args]",
	Short: "Run a command",
	Args:  cobra.ArbitraryArgs,
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		cmdArgs, err := parseRunArgs(cmd, args)
		if err != nil {
			logger.WithError(err).Fatal("Cannot parse arguments")
		}

		ctxLogger := logger.WithFields(logrus.Fields{
			"command":  cmdArgs.Cmd,
			"detach":   cmdArgs.Detach,
			"env-vars": cmdArgs.EnvVars,
			"ports":    cmdArgs.Ports,
		})

		ctxLogger.Info("Running command...")

		err = executor.Execute(cmdArgs.Cmd, &executor.ExecOptions{
			Detach:  cmdArgs.Detach,
			EnvVars: cmdArgs.EnvVars,
			Ports:   cmdArgs.Ports,
		})
		if err != nil {
			ctxLogger.WithError(err).Fatal("Cannot run command in container")
		}

		ctxLogger.Info("Command ran!")
	},
}

func parseRunArgs(cmd *cobra.Command, args []string) (*runArgs, error) {
	detach, err := getBoolArg(cmd, "detach")
	if err != nil {
		return nil, err
	}

	envVars := make(map[string]string)
	rawEnvVars, err := getStringArrayArg(cmd, "env-var")
	if err != nil {
		return nil, err
	}

	for _, rev := range rawEnvVars {
		splitted := strings.Split(rev, "=")
		envVars[splitted[0]] = splitted[1]
	}

	var ports []int
	rawPorts, err := getStringArrayArg(cmd, "port")
	if err != nil {
		return nil, err
	}

	for _, rp := range rawPorts {
		p, err := strconv.Atoi(rp)
		if err != nil {
			return nil, err
		}

		ports = append(ports, p)
	}

	return &runArgs{
		Cmd:     args,
		Detach:  detach,
		EnvVars: envVars,
		Ports:   ports,
	}, nil
}

type runArgs struct {
	Cmd     []string
	Detach  bool
	EnvVars map[string]string
	Ports   []int
}

func init() {
	rootCmd.AddCommand(runCmd)

	runCmd.Flags().BoolP("detach", "d", false, "Whether to detach from container")
	runCmd.Flags().StringArrayP("env-var", "e", []string{}, "Environment variables to set")
	runCmd.Flags().StringArrayP("port", "p", []string{}, "Ports to reach")
}
