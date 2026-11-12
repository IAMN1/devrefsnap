type Greeting = { message: string };

async function getGreeting(url: string): Promise<Greeting> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data: unknown = await response.json();
  if (
    typeof data !== "object" ||
    data === null ||
    !("message" in data) ||
    typeof data.message !== "string"
  ) {
    throw new Error("Expected a JSON object with a string message");
  }

  return { message: data.message };
}

const greeting = await getGreeting("http://127.0.0.1:8000/");
console.log(greeting.message);
