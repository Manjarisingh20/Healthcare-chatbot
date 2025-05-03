document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const responseDiv = document.getElementById("response");

    sendBtn.addEventListener("click", async () => {
        const message = userInput.value.trim();
        if (!message) return;

        responseDiv.innerHTML = "⏳ Thinking...";

        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error("Failed to fetch response from server.");
            }

            const data = await response.json();
            console.log(data); // Log the response data for debugging

            if (data && data.result) {
                responseDiv.innerHTML = data.result; // Display the result from the backend
            } else {
                responseDiv.innerHTML = "Sorry, there was an error processing your request.";
            }

        } catch (error) {
            console.error("Error:", error);
            responseDiv.innerHTML = "An error occurred. Please try again.";
        }
    });
});
