package main

import (
	"fmt"
	"log"

	"example.com/cheatsheet"
)

func main() {
	user, err := cheatsheet.NewUser(" Alice ", "30")
	if err != nil {
		log.Fatal(err)
	}
	if err := user.Rename("Alice Doe"); err != nil {
		log.Fatal(err)
	}
	fmt.Println(cheatsheet.Describe(user))
	fmt.Println(cheatsheet.Contains([]string{"go", "python"}, "go"))
}
