package utils

import "os"

var RESOURCES_PREFIX = "pydockenv_"

func GetCurrentEnv() string {
	return os.Getenv("PYDOCKENV")
}
