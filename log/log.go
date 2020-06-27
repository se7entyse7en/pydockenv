package log

import (
	"fmt"
	"strings"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var Logger = logrus.New()

func SetupLogger(cmd *cobra.Command) error {
	level, err := cmd.Flags().GetString("log-level")
	if err != nil {
		return fmt.Errorf("unrecognized log-level: %w", err)
	}

	var logLevel logrus.Level
	switch l := strings.ToLower(level); l {
	case "trace":
		logLevel = logrus.TraceLevel
	case "debug":
		logLevel = logrus.DebugLevel
	case "info":
		logLevel = logrus.InfoLevel
	case "warn":
		logLevel = logrus.WarnLevel
	case "error":
		logLevel = logrus.ErrorLevel
	case "fatal":
		logLevel = logrus.FatalLevel
	case "panic":
		logLevel = logrus.PanicLevel
	default:
		return fmt.Errorf("unrecognized log-level: %s.", l)
	}

	Logger.SetLevel(logLevel)
	return nil
}
