package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/dependency"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var uninstallCmd = &cobra.Command{
	Use:   "uninstall [package_1] [package_2] ... [package_n]",
	Short: "unInstall packages from args",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		cmdArgs, err := parseUninstallArgs(cmd, args)
		if err != nil {
			logger.WithError(err).Fatal("Cannot parse arguments")
		}

		ctxLogger := logger.WithFields(logrus.Fields{
			"packages": cmdArgs.Packages,
		})
		ctxLogger.Info("Uninstalling packages...")

		if err := dependency.Uninstall(&dependency.Packages{
			RawDependencies: cmdArgs.Packages},
			cmdArgs.Yes,
		); err != nil {
			logger.WithError(err).Fatal("Cannot uninstall packages")
		}

		ctxLogger.Info("Packages uninstalled!")
	},
}

func parseUninstallArgs(cmd *cobra.Command, args []string) (*uninstallArgs, error) {
	yes, err := getBoolArg(cmd, "yes")
	if err != nil {
		return nil, err
	}

	return &uninstallArgs{Packages: args, Yes: yes}, nil
}

type uninstallArgs struct {
	Packages []string
	Yes      bool
}

func init() {
	rootCmd.AddCommand(uninstallCmd)

	uninstallCmd.Flags().BoolP("yes", "y", false, "Don't ask for confirmation")
}
