document.addEventListener('DOMContentLoaded', function() {
  // Create modal elements for day popup
  const modalContainer = document.createElement('div');
  modalContainer.className = 'modal-container';
  modalContainer.style.display = 'none';
  
  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content';
  
  const modalHeader = document.createElement('div');
  modalHeader.className = 'modal-header';
  
  const modalTitle = document.createElement('h2');
  modalTitle.className = 'modal-title';
  modalTitle.textContent = 'Events for this day';
  
  const closeButton = document.createElement('span');
  closeButton.className = 'close-button';
  closeButton.innerHTML = '&times;';
  closeButton.onclick = function() {
    modalContainer.style.display = 'none';
  };
  
  const modalBody = document.createElement('div');
  modalBody.className = 'modal-body';
  
  // Assemble modal
  modalHeader.appendChild(modalTitle);
  modalHeader.appendChild(closeButton);
  modalContent.appendChild(modalHeader);
  modalContent.appendChild(modalBody);
  modalContainer.appendChild(modalContent);
  document.body.appendChild(modalContainer);
  
  // Close modal when clicking outside
  window.onclick = function(event) {
    if (event.target === modalContainer) {
      modalContainer.style.display = 'none';
    }
  };

  // Initialize FullCalendar
  const calendarEl = document.getElementById('calendar');
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'exportButton dayGridMonth,timeGridWeek,timeGridDay'
    },
    customButtons: {
      exportButton: {
        text: '',
        icon: 'download',
        click: function() {
          // Show a message that export is in progress
          addAIMessage('Preparing calendar image for download...');
          
          // Use html2canvas to capture the calendar
          html2canvas(document.getElementById('calendar'), {
            backgroundColor: '#ffffff',
            scale: 2, // Higher scale for better quality
            logging: false,
            useCORS: true
          }).then(canvas => {
            // Convert canvas to data URL
            const imageData = canvas.toDataURL('image/png');
            
            // Create a download link
            const downloadLink = document.createElement('a');
            downloadLink.href = imageData;
            
            // Generate filename with current date and view type
            const today = new Date();
            const viewType = calendar.view.type.replace('Grid', '-');
            const filename = `calendar_${viewType}_${today.getFullYear()}-${(today.getMonth()+1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}.png`;
            
            downloadLink.download = filename;
            
            // Append to body, click, and remove
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            
            // Show success message
            addAIMessage(`Calendar saved as ${filename}`);
          }).catch(error => {
            // Show error message
            addAIMessage('Sorry, there was an error saving the calendar. Please try again.');
            console.error('Error exporting calendar:', error);
          });
        }
      }
    },
    events: [],
    eventTimeFormat: {
      hour: 'numeric',
      minute: '2-digit',
      meridiem: 'short'
    },
    // Feature 1: Day click to show popup with all events
    dateClick: function(info) {
      const clickedDate = info.date;
      const formattedDate = clickedDate.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
      
      // Update modal title
      modalTitle.textContent = `Events for ${formattedDate}`;
      
      // Get all events for the clicked date
      const events = calendar.getEvents().filter(event => {
        const eventDate = new Date(event.start);
        return eventDate.toDateString() === clickedDate.toDateString();
      });
      
      // Clear previous content
      modalBody.innerHTML = '';
      
      // Add events to modal
      if (events.length > 0) {
        const eventList = document.createElement('ul');
        eventList.className = 'event-list';
        
        events.forEach(event => {
          const eventItem = document.createElement('li');
          eventItem.className = 'event-item';
          
          // Format times
          const startTime = new Date(event.start).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          });
          const endTime = new Date(event.end).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          });
          
          // Create event content
          const eventContent = document.createElement('div');
          eventContent.className = 'event-content';
          eventContent.innerHTML = `
            <strong>${event.title}</strong>
            <div class="event-time">${startTime} - ${endTime}</div>
          `;
          
          // Create delete button
          const deleteButton = document.createElement('button');
          deleteButton.className = 'delete-button';
          deleteButton.textContent = 'Cancel';
          deleteButton.onclick = function() {
            if (confirm(`Are you sure you want to cancel "${event.title}"?`)) {
              event.remove();
              addAIMessage(`Cancelled: ${event.title}`);
              
              // Refresh the modal
              eventItem.remove();
              if (eventList.children.length === 0) {
                modalBody.innerHTML = '<p>No events scheduled for this day.</p>';
              }
            }
          };
          
          // Assemble event item
          eventItem.appendChild(eventContent);
          eventItem.appendChild(deleteButton);
          eventList.appendChild(eventItem);
        });
        
        modalBody.appendChild(eventList);
      } else {
        modalBody.innerHTML = '<p>No events scheduled for this day.</p>';
      }
      
      // Show modal
      modalContainer.style.display = 'block';
    },
    // Feature 2: Click on event to cancel it
    eventClick: function(info) {
      if (confirm(`Are you sure you want to cancel "${info.event.title}"?`)) {
        info.event.remove();
        addAIMessage(`Cancelled: ${info.event.title}`);
      }
    }
  });
  calendar.render();

  // Chat functionality
  const chatBox = document.getElementById('chatBox');
  const userInput = document.getElementById('userInput');

  // Add user message to chat
  function addUserMessage(message) {
    const userDiv = document.createElement('div');
    userDiv.className = 'message user';
    userDiv.textContent = message;
    chatBox.appendChild(userDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Add AI message to chat
  function addAIMessage(message) {
    const aiDiv = document.createElement('div');
    aiDiv.className = 'message ai';
    aiDiv.textContent = message;
    chatBox.appendChild(aiDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Handle user input
  userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && userInput.value.trim() !== '') {
      const userMessage = userInput.value.trim();
      addUserMessage(userMessage);
      userInput.value = '';
      
      // Show loading message
      addAIMessage('Scheduling your tasks...');
      
      // Call the backend API
      fetch('http://localhost:8000/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: userMessage })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('API request failed');
        }
        return response.json();
      })
      .then(tasks => {
        // Remove loading message
        chatBox.removeChild(chatBox.lastChild);
        
        // Add success message
        addAIMessage('I\'ve scheduled your tasks! Check the calendar. You can save the calendar as PNG using the download button in the toolbar.');
        
        // Process each new task
        tasks.forEach(task => {
          // Feature 3: Support for time range specification
          // Check if this is a time range task (has both start and end time)
          const hasTimeRange = task.start_time && task.end_time;
          
          // Convert task times to Date objects for comparison
          const taskStart = new Date(`${task.date}T${convertTo24Hour(task.start_time)}`);
          const taskEnd = new Date(`${task.date}T${convertTo24Hour(task.end_time)}`);
          
          // Get all existing events
          const existingEvents = calendar.getEvents();
          
          // Check for time conflicts with existing events
          const conflictingEvents = existingEvents.filter(event => {
            const eventStart = new Date(event.start);
            const eventEnd = new Date(event.end);
            
            // Check if events overlap
            return (
              (taskStart >= eventStart && taskStart < eventEnd) || // New task starts during existing event
              (taskEnd > eventStart && taskEnd <= eventEnd) || // New task ends during existing event
              (taskStart <= eventStart && taskEnd >= eventEnd) // New task completely covers existing event
            );
          });
          
          // Remove any conflicting events
          conflictingEvents.forEach(event => event.remove());
          
          // Add the new task to calendar
          calendar.addEvent({
            title: task.name,
            start: `${task.date}T${convertTo24Hour(task.start_time)}`,
            end: `${task.date}T${convertTo24Hour(task.end_time)}`,
            allDay: false
          });
        });
      })
      .catch(error => {
        // Remove loading message
        chatBox.removeChild(chatBox.lastChild);
        
        // Add error message
        addAIMessage('Sorry, there was an error scheduling your tasks. Please try again.');
        console.error('Error:', error);
      });
    }
  });

  // Helper function to convert 12-hour time format to 24-hour format
  function convertTo24Hour(timeStr) {
    const [time, modifier] = timeStr.split(' ');
    let [hours, minutes] = time.split(':');
    
    if (hours === '12') {
      hours = '00';
    }
    
    if (modifier === 'PM' || modifier === 'pm') {
      hours = parseInt(hours, 10) + 12;
    }
    
    return `${hours}:${minutes}:00`;
  }
});
