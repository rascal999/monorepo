const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;

function validateApiKey() {
  console.log('Validating API key...');
  console.log('API Key value:', OPENROUTER_API_KEY ? 'Present (length: ' + OPENROUTER_API_KEY.length + ')' : 'Missing');
  console.log('Available env vars:', Object.keys(import.meta.env));
  
  if (!OPENROUTER_API_KEY) {
    console.error('OpenRouter API key not found in environment variables');
    throw new Error('OpenRouter API key not found. Please check your .env file and ensure VITE_OPENROUTER_API_KEY is set correctly.');
  }
  
  if (OPENROUTER_API_KEY === 'your_api_key_here') {
    console.error('Default API key detected. Please replace with actual key.');
    throw new Error('Please replace the default API key with your actual OpenRouter API key.');
  }
}

export async function fetchModels() {
  console.log('Fetching available models from OpenRouter API');
  validateApiKey();

  try {
    const response = await fetch('https://openrouter.ai/api/v1/models', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'HTTP-Referer': window.location.href,
      }
    });

    const data = await response.json();
    console.log('Models API response:', data);
    
    if (!response.ok) {
      console.error('API error:', data);
      throw new Error(data.error?.message || `API request failed with status ${response.status}`);
    }

    console.log('Successfully fetched models:', data.data);
    return data.data;
  } catch (error) {
    console.error('Error in fetchModels:', error);
    console.error('Stack trace:', error.stack);
    throw error;
  }
}

export async function fetchChatCompletion(messages, model = 'openai/gpt-4-turbo', onStream) {
  try {
    console.log('Fetching chat completion with messages:', messages);
    validateApiKey();
    const requestBody = {
      model,
      messages,
      stream: Boolean(onStream)
    };
    console.log('Request body:', requestBody);

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'HTTP-Referer': window.location.href,
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const data = await response.json();
      console.error('API error:', {
        status: response.status,
        statusText: response.statusText,
        data,
        messages
      });
      throw new Error(data.error?.message || `API request failed with status ${response.status}`);
    }

    if (requestBody.stream) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;
          if (line.trim() === 'data: [DONE]') {
            // Return the complete message
            return { role: 'assistant', content: fullContent };
          }

          // Skip empty lines or lines without data prefix
          if (!line.startsWith('data: ')) continue;
          
          const jsonStr = line.replace(/^data: /, '').trim();
          if (!jsonStr || jsonStr === '[DONE]') continue;
          
          try {
            const data = JSON.parse(jsonStr);
            const content = data.choices?.[0]?.delta?.content;
            if (content) {
              fullContent += content;
              if (onStream) {
                onStream(content);
              }
            }
          } catch (e) {
            console.warn('Error parsing stream line:', e, 'Line:', jsonStr);
            // Continue processing other lines even if one fails
            continue;
          }
        }
      }
      
      // Return the complete message if we exit the loop without [DONE]
      return { role: 'assistant', content: fullContent };
    } else {
      // Handle non-streaming response
      const data = await response.json();
      console.log('API response:', data);
      
      const content = data.choices?.[0]?.message?.content;
      if (!content) {
        console.error('No content in response:', data);
        throw new Error('No content in response');
      }
      
      console.log('Returning message:', data.choices[0].message);
      return data.choices[0].message;
    }
  } catch (error) {
    console.error('Error in fetchChatCompletion:', {
      error: error.message,
      type: error.name,
      stack: error.stack,
      messages,
      model
    });
    throw new Error(`Chat completion failed: ${error.message}`);
  }
}
