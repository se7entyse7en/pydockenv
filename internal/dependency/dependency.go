package dependency

import (
	"fmt"

	"github.com/docker/docker/api/types"
	"github.com/se7entyse7en/pydockenv/internal/executor"
)

type Requirements struct {
	FileName string
	Packages
}

type Packages struct {
	Dependencies    map[string]string
	RawDependencies []string
}

func Install(requirements *Requirements) error {
	cmd := buildInstallCmd(requirements)
	err := executor.Execute(cmd, &executor.ExecOptions{})
	if err != nil {
		return fmt.Errorf("cannot install requirements in container: %w", err)
	}

	return nil
}

func InstallForContainer(container types.ContainerJSON, requirements *Requirements) error {
	cmd := buildInstallCmd(requirements)
	err := executor.ExecuteForContainer(container, cmd,
		&executor.ExecOptions{ByPassCheck: true})
	if err != nil {
		return fmt.Errorf("cannot install requirements in container: %w", err)
	}

	return nil
}

func Uninstall(packages *Packages, yes bool) error {
	cmd := []string{"pip", "uninstall"}
	cmd = append(cmd, parsePackages(packages)...)
	if yes {
		cmd = append(cmd, "-y")
	}

	err := executor.Execute(cmd, &executor.ExecOptions{})
	if err != nil {
		return fmt.Errorf("cannot uninstall requirements in container: %w", err)
	}

	return nil
}

func ListPackage() error {
	err := executor.Execute([]string{"pip", "freeze"}, &executor.ExecOptions{})
	if err != nil {
		return fmt.Errorf("cannot list packages in container: %w", err)
	}

	return nil
}

func buildInstallCmd(requirements *Requirements) []string {
	cmd := []string{"pip", "install"}
	if requirements.FileName != "" {
		cmd = append(cmd, "-r", requirements.FileName)
	} else {
		cmd = append(cmd, parsePackages(&requirements.Packages)...)
	}

	return cmd
}

func parsePackages(packages *Packages) []string {
	if len(packages.RawDependencies) > 0 {
		return packages.RawDependencies
	}

	var parsedPackages []string
	for p, v := range packages.Dependencies {
		parsedPackages = append(parsedPackages, fmt.Sprintf("%s%s", p, v))
	}

	return parsedPackages
}
