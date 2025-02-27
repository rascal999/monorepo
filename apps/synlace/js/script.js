document.addEventListener('DOMContentLoaded', () => {
    const commandInput = document.getElementById('command-input');
    const cursor = document.getElementById('cursor');
    const commandLine = document.querySelector('.command-line');
    
    // No sample data needed for the demo
    
    // No command processing needed for the demo
    
    // Typing animation
    function typeText(element, text, index = 0, callback) {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            setTimeout(() => {
                typeText(element, text, index + 1, callback);
            }, Math.random() * 25 + 25); // Slightly slower typing speed
        } else if (callback) {
            callback();
        }
    }
    
    // Function to display a command and then fade it out
    function displayCommand(command, callback) {
        // Clear any existing text and ensure no fade class is active
        commandInput.textContent = '';
        commandLine.classList.remove('fade-out');
        
        // Type the command
        typeText(commandInput, command, 0, () => {
            // After typing is complete, wait a shorter moment
            setTimeout(() => {
                // Fade out the command
                commandLine.classList.add('fade-out');
                
                // After fading out, clear and prepare for next command
                setTimeout(() => {
                    commandInput.textContent = '';
                    
                    if (callback) callback();
                }, 800); // Slightly faster fade out transition
            }, 1500); // Display the command for a shorter time before fading
        });
    }
    
    // Simulate initial commands on page load
    setTimeout(() => {
        const demoCommands = [
            // Simple tool-specific commands
            'Show my assigned Jira tickets in the SALES project',
            'Summarize today\'s #general Slack messages',
            'Find Q1 sales forecast docs in Drive shared with me',
            'List open GitLab merge requests for the frontend repo',
            
            // Natural language interpretation
            'What did the design team discuss in Slack yesterday?',
            'When is the next marketing meeting in my Google Calendar?',
            'Who\'s working on the homepage redesign in Jira?',
            'How many sales leads did we get in Salesforce this week?',
            
            // Multi-tool commands
            'Share latest sales report from Drive with marketing team in Slack',
            'Create Jira ticket from yesterday\'s Slack conversation with @sarah',
            'Find Drive docs mentioning "Q2 sales" and notify @david in Slack',
            
            // Data transformation between tools
            'Create GitLab issues from feedback in Teams #customer-support',
            'Send Q1 chart from Salesforce to marketing@company.com',
            
            // Additional tool-specific commands
            'Show blocked Jira tickets in the MARKETING project',
            'Summarize yesterday\'s #engineering Slack messages',
            'Find product roadmap docs in Drive shared by @michael',
            'List merged GitLab merge requests from last sprint',
            
            // Additional natural language queries
            'What features are planned for the next release?',
            'When did we last update the customer onboarding flow?',
            'Who\'s responsible for the payment gateway integration?',
            'How many customer issues were resolved this month?',
            
            // Additional multi-tool commands
            'Create Jira subtasks from product meeting notes in Drive',
            'Find Slack messages about performance issues and create Jira ticket'
        ];
        
        // Function to shuffle array
        function shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
        }
        
        // Shuffle the commands
        const shuffledCommands = shuffleArray([...demoCommands]);
        let commandIndex = 0;
        
        function runNextCommand() {
            if (commandIndex < shuffledCommands.length) {
                const command = shuffledCommands[commandIndex];
                
                // Display the command with fade in/out effect
                displayCommand(command, () => {
                    commandIndex++;
                    
                    // If we've shown all commands, reshuffle and start again
                    if (commandIndex >= shuffledCommands.length) {
                        commandIndex = 0;
                        // Reshuffle for next round
                        shuffleArray(shuffledCommands);
                    }
                    
                    // Shorter wait before showing the next command
                    setTimeout(runNextCommand, 400);
                });
            }
        }
        
        runNextCommand();
    }, 1500);
    
    // We don't need keyboard event listeners for the demo
    // as we're just showing the animated commands automatically
});