const MODEL_NAME = "text-bison@001"; // Replace "gemini-l.e-pro" with Google Vertex AI model
const API_KEY = "AlzaSyCgbdDzk5iBJDMk-dcNvyM7k9wsAihZctc"; // Replace with your Google API key

async function callVertexAI(query) {
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/publishers/google/models/${MODEL_NAME}:predict`;

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${API_KEY}`, // Use your API key
  };

  const body = JSON.stringify({
    instances: [{ content: query }], // Your query to the model
    parameters: {
      temperature: 0.7, // Adjust for creativity
      maxOutputTokens: 300, // Limit output length
    },
  });

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: body,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch data. Status: ${response.status}`);
    }

    const data = await response.json();

    // Display the fetched response
    console.log("Model response:", data.predictions[0].content);
    return data.predictions[0].content.trim(); // Return response content
  } catch (error) {
    console.error("Error:", error.message);
    return `Error: ${error.message}`;
  }
}

// Test the function
callVertexAI("What are some home remedies for headaches?");
