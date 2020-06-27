package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/environment"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/spf13/cobra"
)

var listEnvironmentsCmd = &cobra.Command{
	Use:   "list-environments",
	Short: "List all the virtual environments",
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		logger.Info("Listing virtual environments...")

		if err := environment.ListEnvironments(); err != nil {
			logger.WithError(err).Fatal("Cannot list virtual environments")
		}

		logger.Info("Virtual environments listed!")
	},
}

func init() {
	rootCmd.AddCommand(listEnvironmentsCmd)
}
