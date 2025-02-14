local cjson = require "cjson"
local http = require "resty.http"

-- Function to build raw request string
local function build_raw_request()
    local req = ngx.req
    local headers = ngx.req.get_headers()
    local method = ngx.req.get_method()
    local uri = ngx.req.uri
    
    -- Start with request line
    local raw_request = string.format("%s %s HTTP/1.1\n", method, uri)
    
    -- Add headers
    for k, v in pairs(headers) do
        raw_request = raw_request .. string.format("%s: %s\n", k, v)
    end
    
    -- Add body if present
    ngx.req.read_body()
    local body = ngx.req.get_body_data()
    if body then
        raw_request = raw_request .. "\n" .. body
    end
    
    return raw_request
end

-- Function to block IP
local function block_ip(ip)
    ngx.log(ngx.INFO, "Blocking IP: ", ip)
    
    -- Append to blocked IPs file
    local f = io.open("/etc/nginx/blocked_ips.conf", "a")
    if f then
        f:write(string.format("%s 1;\n", ip))
        f:close()
        
        -- Reload nginx
        os.execute("nginx -s reload")
    end
end

-- Main function
local function classify_request()
    local ok, raw_request = pcall(build_raw_request)
    if not ok then
        ngx.log(ngx.ERR, "Failed to build raw request: ", raw_request)
        return
    end

    local client_ip = ngx.var.remote_addr
    
    ngx.log(ngx.INFO, "Processing request from ", client_ip, ":\n", raw_request)
    
    -- Skip static files and health checks
    if string.match(ngx.var.uri, "%.%w+$") or ngx.var.uri == "/health" then
        ngx.log(ngx.INFO, "Skipping static file or health check")
        return
    end
    
    -- Create HTTP client
    local httpc = http.new()
    httpc:set_timeout(5000)  -- 5 second timeout
    
    -- Call Ollama
    local res, err = httpc:request_uri("http://host.docker.internal:11343/api/generate", {
        method = "POST",
        body = cjson.encode({
            model = "qwen2.5:7b-instruct",
            prompt = string.format([[Analyze this HTTP request and determine if it's suspicious or malicious:

%s

Respond with either 'suspicious' or 'normal' based on:
1. If it's trying to access admin/system paths
2. If it contains SQL injection attempts
3. If it has suspicious headers or payloads
4. If it's probing for vulnerabilities
5. If it's attempting to exploit common web vulnerabilities

Response:]], raw_request)
        }),
        headers = {
            ["Content-Type"] = "application/json",
        },
    })
    
    if not res then
        ngx.log(ngx.ERR, "Failed to call Ollama: ", err)
        return
    end
    
    -- Parse response
    local success, result = pcall(cjson.decode, res.body)
    if success and result.response then
        ngx.log(ngx.INFO, "Ollama response: ", result.response)
        
        -- Check if suspicious
        if string.find(string.lower(result.response), "suspicious") then
            block_ip(client_ip)
        end
    else
        ngx.log(ngx.ERR, "Failed to parse Ollama response: ", res.body)
    end
end

-- Run classification in protected call
local ok, err = pcall(classify_request)
if not ok then
    ngx.log(ngx.ERR, "Error in classify_request: ", err)
end