package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/environment"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var removeCmd = &cobra.Command{
	Use:   "remove [environment-name]",
	Short: "Remove a virtual environment",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		cmdArgs, err := parseRemoveArgs(cmd, args)
		if err != nil {
			logger.WithError(err).Fatal("Cannot parse arguments")
		}

		ctxLogger := logger.WithFields(logrus.Fields{
			"name": cmdArgs.Name,
		})
		ctxLogger.Info("Removing virtual environment...")

		if err := environment.Remove(cmdArgs.Name); err != nil {
			logger.WithError(err).Fatal("Cannot remove virtual environment")
		}

		ctxLogger.Info("Virtual environment removed!")
	},
}

func parseRemoveArgs(cmd *cobra.Command, args []string) (*removeArgs, error) {
	name := args[0]
	return &removeArgs{Name: name}, nil
}

type removeArgs struct {
	Name string
}

func init() {
	rootCmd.AddCommand(removeCmd)
}
