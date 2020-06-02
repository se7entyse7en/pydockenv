package cmd

import (
	"github.com/se7entyse7en/pydockenv/internal/executor"
	"github.com/se7entyse7en/pydockenv/log"
	"github.com/spf13/cobra"
)

var shellCmd = &cobra.Command{
	Use:   "shell [args]",
	Short: "Run Python",
	Args:  cobra.ArbitraryArgs,
	Run: func(cmd *cobra.Command, args []string) {
		logger := log.Logger
		err := log.SetupLogger(cmd)
		if err != nil {
			logger.WithError(err).Fatal("Cannot setup logger")
		}

		logger.Info("Running Python...")

		command := []string{"python"}
		command = append(command, args...)
		err = executor.Execute(command, &executor.ExecOptions{})
		if err != nil {
			logger.WithError(err).Fatal("Cannot run Python in container")
		}

		logger.Info("Python ran!")
	},
}

func init() {
	rootCmd.AddCommand(shellCmd)
}
