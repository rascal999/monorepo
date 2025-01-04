const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;

export async function fetchChatCompletion(messages) {
  if (!OPENROUTER_API_KEY) {
    throw new Error('OpenRouter API key not found');
  }

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'HTTP-Referer': window.location.href,
    },
    body: JSON.stringify({
      model: 'google/palm-2-chat-bison',
      messages
    })
  });

  const data = await response.json();
  
  if (data.error) {
    throw new Error(data.error.message || 'API request failed');
  }
  
  const content = data.choices?.[0]?.message?.content;
  if (!content) {
    throw new Error('No content in response');
  }
  
  return data.choices[0].message;
}
