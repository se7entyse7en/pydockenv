package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/dependency"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/spf13/cobra"
)

var listPackagesCmd = &cobra.Command{
	Use:   "list-packages",
	Short: "List the packages installed for the current virtual environments",
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		logger.Info("Listing packages...")

		if err := dependency.ListPackage(); err != nil {
			logger.WithError(err).Fatal("Cannot list packages")
		}

		logger.Info("Packages listed!")
	},
}

func init() {
	rootCmd.AddCommand(listPackagesCmd)
}
