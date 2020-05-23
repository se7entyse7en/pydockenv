package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/environment"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/spf13/cobra"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show the current active virtual environment",
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		if err := environment.Status(); err != nil {
			logger.WithError(err).Fatal("Cannot show current active virtual environment")
		}
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)
}
