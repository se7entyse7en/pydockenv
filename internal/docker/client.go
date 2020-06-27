package docker

import "github.com/docker/docker/client"

func getClient() (*client.Client, error) {
	return client.NewClientWithOpts(client.FromEnv)
}
