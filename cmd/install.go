package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/dependency"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var installCmd = &cobra.Command{
	Use:   "install [package_1] [package_2] ... [package_n]",
	Short: "Install packages from args or from a requirements file",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		cmdArgs, err := parseInstallArgs(cmd, args)
		if err != nil {
			logger.WithError(err).Fatal("Cannot parse arguments")
		}

		ctxLogger := logger.WithFields(logrus.Fields{
			"packages": cmdArgs.Packages,
			"file":     cmdArgs.RequirementsFile,
		})
		ctxLogger.Info("Installing packages...")

		if err := dependency.Install(&dependency.Requirements{
			FileName: cmdArgs.RequirementsFile,
			Packages: dependency.Packages{RawDependencies: cmdArgs.Packages},
		}); err != nil {
			logger.WithError(err).Fatal("Cannot install packages")
		}

		ctxLogger.Info("Packages installed!")
	},
}

func parseInstallArgs(cmd *cobra.Command, args []string) (*installArgs, error) {
	requirementsFile, err := getStringArg(cmd, "file")
	if err != nil {
		return nil, err
	}

	return &installArgs{
		Packages:         args,
		RequirementsFile: requirementsFile,
	}, nil
}

type installArgs struct {
	Packages         []string
	RequirementsFile string
}

func init() {
	rootCmd.AddCommand(installCmd)

	installCmd.Flags().StringP("file", "f", "", "Requirements file")
}
