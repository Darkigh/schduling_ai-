import OpenAI from "openai";
const chatBox = document.getElementById("chatBox");
const input = document.getElementById("userInput");
let calendar;

// Add message to UI
function addMessage(text, sender = 'ai') {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.innerText = (sender === 'user' ? 'Me: ' : 'AI Schedule: ') + text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Setup FullCalendar
document.addEventListener('DOMContentLoaded', () => {
  const calendarEl = document.getElementById('calendar');
  calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    editable: true,
    eventClick: function(info) {
      if (confirm(`Delete "${info.event.title}"?`)) {
        info.event.remove();
      }
    },
    events: []
  });
  calendar.render();
});

// Input handler
input.addEventListener("keydown", async (e) => {
  if (e.key === 'Enter') {
    const prompt = input.value.trim();
    if (!prompt) return;

    addMessage(prompt, 'user');
    input.value = "";

    const OPENAI_API_KEY = "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"; // 👈 Replace this

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: `You are an AI scheduling assistant. The user will enter natural language describing appointments, events, or tasks.
Your job is to extract structured event data from the message. For each event, provide:

- title: A short description of the task or appointment
- start: The full ISO 8601 datetime (e.g. 2025-05-15T15:00:00)
- end: The ISO 8601 datetime for when the event ends (assume 1 hour duration if not specified)

Return your result as a JSON object named "events", containing an array of event objects. Do not include extra text or explanations.`
          },
          { role: "user", content: prompt }
        ]
      })
    });

    const data = await response.json();
    let jsonString = data.choices[0].message.content;

    try {
      console.log("AI response:", jsonString);
      const parsed = JSON.parse(jsonString);
      const tasks = parsed.events;

      tasks.forEach(task => {
        calendar.addEvent({
          title: task.title,
          start: task.start,
          end: task.end
        });
      });

      addMessage("✅ Events added to your calendar.");
    } catch (err) {
      console.error("JSON parsing failed:", err);
      addMessage("⚠️ Could not parse AI response.");
    }
  }
});