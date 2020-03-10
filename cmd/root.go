package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "pydockenv",
	Short: "A CLI tool to handle Python virtual environments",
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func getStringArg(cmd *cobra.Command, argName string) (string, error) {
	value, err := cmd.Flags().GetString(argName)
	if err != nil {
		return "", fmt.Errorf("cannot read %s: %w", argName, err)
	}

	return value, nil
}

func init() {
	rootCmd.PersistentFlags().StringP("log-level", "l", "info", "Log level")
}
