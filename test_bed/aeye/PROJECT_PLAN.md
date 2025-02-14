# AEye Architecture Redesign

## Overview
Instead of using a complex nginx module, we'll use a simpler approach with a Python script monitoring nginx logs and managing IP blocking.

## Components

### 1. Nginx Configuration
- Configure JSON format logging for access logs
- Include request body in logs for POST requests
- Use geo module for IP blocking
- Use map module to conditionally block IPs
- Real-time config reloading for IP updates

### 2. Python Monitor Script
- Tail nginx access log file
- Parse JSON log entries
- Filter out static files and socket.io
- Send suspicious requests to Ollama
- Update nginx blocked IPs list
- Reload nginx config when needed

### 3. IP Blocking
- Use nginx geo module to define blocked IPs
- Store blocked IPs in a separate config file
- Python script updates this file
- Nginx includes this file in main config
- Use nginx's reload capability for updates

### 4. Implementation Plan

#### Phase 1: Nginx Setup
1. Configure JSON logging
```nginx
log_format json_combined escape=json
    '{'
    '"time_local":"$time_local",'
    '"remote_addr":"$remote_addr",'
    '"request_method":"$request_method",'
    '"request_uri":"$request_uri",'
    '"status": "$status",'
    '"body_bytes_sent":"$body_bytes_sent",'
    '"request_time":"$request_time",'
    '"http_referrer":"$http_referer",'
    '"http_user_agent":"$http_user_agent",'
    '"request_body":"$request_body"'
    '}';
```

2. Setup IP blocking
```nginx
geo $blocked_ip {
    default 0;
    include /etc/nginx/blocked_ips.conf;
}

map $blocked_ip $blocked {
    0 0;
    1 1;
}
```

#### Phase 2: Python Monitor
1. Log monitoring
```python
def monitor_log():
    with open('/var/log/nginx/access.log', 'r') as f:
        f.seek(0, 2)  # Go to end
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            process_log_entry(json.loads(line))
```

2. Request classification
```python
def process_log_entry(entry):
    # Skip static files
    if re.match(r'\.(css|js|jpg|png|gif|ico|woff2?)$', entry['request_uri']):
        return
        
    # Skip socket.io
    if entry['request_uri'].startswith('/socket.io/'):
        return
        
    # Classify with Ollama
    result = classify_request(entry)
    if result['suspicious']:
        block_ip(entry['remote_addr'])
```

3. IP blocking
```python
def block_ip(ip):
    with open('/etc/nginx/blocked_ips.conf', 'a') as f:
        f.write(f'{ip} 1;\n')
    subprocess.run(['nginx', '-s', 'reload'])
```

### Benefits
1. Simpler implementation
2. Easier to maintain and debug
3. Uses nginx's built-in capabilities
4. Non-blocking request processing
5. Real-time IP blocking
6. Better separation of concerns

### Configuration Options
```nginx
# nginx.conf
access_log /var/log/nginx/access.log json_combined;
client_max_body_size 1m;
client_body_buffer_size 1m;
```

### Monitoring
- Watch nginx error log for reload status
- Monitor blocked IPs count
- Track classification results
- Log processing latency
- Memory usage stats