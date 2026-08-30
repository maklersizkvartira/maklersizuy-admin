with open('admin-frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix unblock / reject listing endpoints to use PATCH /listings/:id/status
content = content.replace("fetch(`${API_BASE}/admin/listings/${id}/unblock`, {", "fetch(`${API_BASE}/listings/${id}/status`, {")
content = content.replace("fetch(`${API_BASE}/admin/listings/${id}/reject`, {", "fetch(`${API_BASE}/listings/${id}/status`, {")

# In unblock function, we need to pass status: 'APPROVED' in the body.
# Let's see how they were defined.
