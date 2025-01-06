const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;

function validateApiKey() {
  if (!OPENROUTER_API_KEY) {
    console.error('OpenRouter API key not found in environment variables');
    console.log('Available env vars:', import.meta.env);
    throw new Error('OpenRouter API key not found. Please check your .env file and ensure VITE_OPENROUTER_API_KEY is set correctly.');
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

export async function fetchChatCompletion(messages, model = 'openai/gpt-4-turbo') {
  console.log('Fetching chat completion with messages:', messages);
  
  validateApiKey();

  try {
    const requestBody = {
      model,
      messages
    };
    console.log('Request body:', requestBody);

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'HTTP-Referer': window.location.href,
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();
    console.log('API response:', data);
    
    if (!response.ok) {
      console.error('API error:', data);
      throw new Error(data.error?.message || `API request failed with status ${response.status}`);
    }
    
    const content = data.choices?.[0]?.message?.content;
    if (!content) {
      console.error('No content in response:', data);
      throw new Error('No content in response');
    }
    
    console.log('Returning message:', data.choices[0].message);
    return data.choices[0].message;
  } catch (error) {
    console.error('Error in fetchChatCompletion:', error);
    console.error('Stack trace:', error.stack);
    throw error;
  }
}
