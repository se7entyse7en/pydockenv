package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/environment"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var activateCmd = &cobra.Command{
	Use:   "activate [environment-name]",
	Short: "Activate a virtual environment",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		cmdArgs, err := parseActivateArgs(cmd, args)
		if err != nil {
			logger.WithError(err).Fatal("Cannot parse arguments")
		}

		ctxLogger := logger.WithFields(logrus.Fields{
			"name": cmdArgs.Name,
		})
		ctxLogger.Info("Activating virtual environment...")

		if err := environment.Activate(cmdArgs.Name); err != nil {
			logger.WithError(err).Fatal("Cannot activate virtual environment")
		}

		ctxLogger.Info("Virtual environment activated!")
	},
}

func parseActivateArgs(cmd *cobra.Command, args []string) (*activateArgs, error) {
	name := args[0]
	return &activateArgs{Name: name}, nil
}

type activateArgs struct {
	Name string
}

func init() {
	rootCmd.AddCommand(activateCmd)
}
