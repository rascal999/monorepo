const runtime = {
  async handler(params, context = {}) {
    const { expression } = params;
    const { introspect = console.log } = context;

    try {
      // Log thought process
      introspect(`Calculating expression: ${expression}`);

      // Sanitize input to only allow basic arithmetic
      const sanitized = expression.replace(/[^0-9+\-*/(). ]/g, '');
      
      // Evaluate the expression
      const result = eval(sanitized);
      
      // Format the result
      const formattedExpression = expression
        .replace(/\*/g, ' times ')
        .replace(/\//g, ' divided by ')
        .replace(/\+/g, ' plus ')
        .replace(/\-/g, ' minus ');
      
      return {
        success: true,
        message: `The result of ${formattedExpression} is ${result}`
      };
    } catch (error) {
      return {
        success: false,
        message: "Invalid arithmetic expression"
      };
    }
  }
};

module.exports = { runtime };