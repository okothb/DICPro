# Netlify Environment Setup

## Required Environment Variables

For the offline-first hash storage system to work on Netlify, you need to configure these environment variables in your Netlify dashboard:

### 1. Upstash Redis Configuration

```bash
UPSTASH_REDIS_REST_URL=https://your-redis-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-redis-token-here
```

**How to get these:**
1. Go to [Upstash Console](https://console.upstash.com/)
2. Create a new Redis database
3. Copy the REST URL and Token from the database details

### 2. Optional: VirusTotal API (for enhanced security)

```bash
VIRUSTOTAL_API_KEY=your-virustotal-api-key
```

## Setting Environment Variables in Netlify

1. Go to your Netlify site dashboard
2. Navigate to **Site settings** → **Environment variables**
3. Click **Add variable** for each required variable
4. Enter the variable name and value
5. Click **Save**

## Testing the Configuration

After setting up the environment variables:

1. Deploy your site to Netlify
2. Test the API endpoints:
   - `https://your-site.netlify.app/.netlify/functions/api/health`
   - `https://your-site.netlify.app/.netlify/functions/api/hash/sync/status`

## Troubleshooting

### "Redis not available" errors
- Check that `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` are set correctly
- Verify the Redis instance is active in Upstash console
- Check Netlify function logs for connection errors

### "Module not found" errors
- Ensure `netlify_requirements.txt` includes all necessary dependencies
- Check that the build command is set correctly in `netlify.toml`
- Verify Python version compatibility (3.9 recommended)

### Hash storage not working
- Verify Redis connection in function logs
- Test hash endpoints directly via API
- Check that the hash management endpoints are properly routed

## Local Development

For local development, create a `.env` file:

```bash
UPSTASH_REDIS_REST_URL=https://your-redis-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-redis-token-here
```

Then run:
```bash
netlify dev
```

This will simulate the Netlify environment locally.