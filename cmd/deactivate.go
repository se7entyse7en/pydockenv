package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/environment"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/spf13/cobra"
)

var deactivateCmd = &cobra.Command{
	Use:   "deactivate",
	Short: "Deactivate the current virtual environment",
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		logger.Info("Deactivating virtual environment...")

		if err := environment.Deactivate(); err != nil {
			logger.WithError(err).Fatal("Cannot deactivate virtual environment")
		}

		logger.Info("Virtual environment deactivated!")
	},
}

func init() {
	rootCmd.AddCommand(deactivateCmd)
}
