const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;

export async function fetchChatCompletion(messages, model = 'openai/gpt-4-turbo') {
  console.log('Fetching chat completion with messages:', messages);
  
  if (!OPENROUTER_API_KEY) {
    console.error('OpenRouter API key not found');
    throw new Error('OpenRouter API key not found');
  }

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
}
