const API_BASE = '/api/v1';

// --- Utility Functions ---

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers
    };

    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
        // Token might be expired or invalid
        removeToken();
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
        throw new Error('Unauthorized');
    }
    
    return response;
}

function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);
    const diffDay = Math.round(diffHour / 24);

    if (diffSec < 60) return `${diffSec}s`;
    if (diffMin < 60) return `${diffMin}m`;
    if (diffHour < 24) return `${diffHour}h`;
    return `${date.toLocaleString('default', { month: 'short' })} ${date.getDate()}`;
}

// --- Authentication ---

document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the login page
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        setupAuthForms();
    }

    // Check if user is logged in for protected pages
    const token = getToken();
    const path = window.location.pathname;
    
    if (!token && path !== '/') {
        window.location.href = '/';
    } else if (token) {
        // Validate token is still valid (user might have been deleted)
        if (path !== '/') {
            apiFetch('/auth/me').then(res => {
                if (!res.ok) {
                    removeToken();
                    localStorage.removeItem('user');
                    window.location.href = '/';
                } else {
                    setupUserInterface();
                    if (path === '/feed') {
                        loadFeed();
                        setupComposePost();
                    } else if (path.length > 1 && path !== '/feed') {
                        loadProfile();
                    }
                }
            }).catch(() => {
                setupUserInterface();
                if (path === '/feed') {
                    loadFeed();
                    setupComposePost();
                } else if (path.length > 1 && path !== '/feed') {
                    loadProfile();
                }
            });
        }
    }
});

function setupAuthForms() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const emailOrUsername = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorDiv = document.getElementById('login-error');

        // Note: The backend expects 'email' or 'username'. We will try sending as email first, 
        // if it lacks '@', we could send as username. Let's send as email or adjust based on backend API.
        // Assuming backend auth/login accepts email or username. 
        // Looking at typical implementations, they usually check if it's email or username in the backend.
        // Let's send username or email. We'll use email field for both.
        
        const payload = emailOrUsername.includes('@') ? 
            { email: emailOrUsername, password } : 
            { username: emailOrUsername, password };

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (res.ok) {
                setToken(data.data.access_token);
                // Also save user info
                localStorage.setItem('user', JSON.stringify(data.data.user));
                window.location.href = '/feed';
            } else {
                errorDiv.textContent = data.message || 'Login failed.';
                errorDiv.classList.remove('hidden');
            }
        } catch (err) {
            errorDiv.textContent = 'Network error.';
            errorDiv.classList.remove('hidden');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;
        const errorDiv = document.getElementById('register-error');

        if (password !== confirmPassword) {
            errorDiv.textContent = 'Passwords do not match.';
            errorDiv.classList.remove('hidden');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, confirm_password: confirmPassword })
            });
            const data = await res.json();

            if (res.ok) {
                // Now log them in
                const loginRes = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const loginData = await loginRes.json();
                if(loginRes.ok) {
                    setToken(loginData.data.access_token);
                    localStorage.setItem('user', JSON.stringify(loginData.data.user));
                    window.location.href = '/feed';
                }
            } else {
                errorDiv.textContent = data.message || 'Registration failed.';
                errorDiv.classList.remove('hidden');
            }
        } catch (err) {
            console.error(err);
            errorDiv.textContent = 'Error: ' + err.message;
            errorDiv.classList.remove('hidden');
        }
    });
}

function setupUserInterface() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        const miniProfile = document.getElementById('current-user-miniprofile');
        if (miniProfile) {
            miniProfile.style.display = 'flex';
            document.getElementById('current-user-display-name').textContent = user.username;
            document.getElementById('current-user-username').textContent = `@${user.username}`;
            
            miniProfile.addEventListener('click', () => {
                const menu = document.getElementById('logout-menu');
                menu.classList.toggle('hidden');
            });

            document.getElementById('logout-btn').addEventListener('click', () => {
                removeToken();
                localStorage.removeItem('user');
                window.location.href = '/';
            });
            
            // Set nav profile link
            const profileLink = document.getElementById('nav-profile');
            if(profileLink) {
                profileLink.href = `/${user.username}`;
            }
        }
    }
}

// --- Feed & Posts ---

async function loadFeed() {
    const container = document.getElementById('feed-container');
    if (!container) return;
    
    try {
        // Fetch personalized feed
        const res = await apiFetch('/feed');
        const data = await res.json();
        
        container.innerHTML = ''; // clear spinner
        
        const posts = data.data ? data.data.posts : (data.posts || []);
        if (posts && posts.length > 0) {
            posts.forEach(post => {
                container.appendChild(createPostElement(post));
            });
        } else {
            container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-secondary);">No posts yet. Follow people or post something!</div>';
        }
    } catch (err) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--error-color);">Failed to load feed.</div>';
    }
}

function createPostElement(post) {
    const div = document.createElement('div');
    div.className = 'post';
    
    // Fallbacks if backend schema differs slightly
    const username = (post.author && post.author.username) || (post.user && post.user.username) || 'unknown';
    const content = post.content || '';
    const likes = post.likes_count || 0;
    const comments = post.comments_count || 0;
    const isLiked = post.liked_by_me || post.is_liked_by_current_user || false;
    
    div.innerHTML = `
        <div class="avatar-placeholder" style="width: 48px; height: 48px; cursor:pointer;" onclick="window.location.href='/${username}'"></div>
        <div class="post-content-container">
            <div class="post-header">
                <a href="/${username}" class="post-display-name">${username}</a>
                <span class="post-username">@${username}</span>
                <span class="post-time">· ${formatTime(post.created_at || new Date())}</span>
            </div>
            <div class="post-text">${escapeHTML(content)}</div>
            <div class="post-actions">
                <div class="post-action action-reply">
                    <i class="ph ph-chat-circle"></i>
                    <span>${comments > 0 ? comments : ''}</span>
                </div>
                <div class="post-action action-repost">
                    <i class="ph ph-arrows-clockwise"></i>
                    <span></span>
                </div>
                <div class="post-action action-like ${isLiked ? 'liked' : ''}" data-id="${post.id || post.post_id}">
                    <i class="${isLiked ? 'ph-fill ph-heart' : 'ph ph-heart'}"></i>
                    <span class="like-count">${likes > 0 ? likes : ''}</span>
                </div>
                <div class="post-action action-share">
                    <i class="ph ph-export"></i>
                </div>
            </div>
        </div>
    `;
    
    // Add like listener
    const likeBtn = div.querySelector('.action-like');
    likeBtn.addEventListener('click', async (e) => {
        e.stopPropagation(); // prevent post click
        const postId = likeBtn.getAttribute('data-id');
        try {
            const method = likeBtn.classList.contains('liked') ? 'DELETE' : 'POST';
            const res = await apiFetch(`/posts/${postId}/like`, { method });
            if (res.ok) {
                likeBtn.classList.toggle('liked');
                const icon = likeBtn.querySelector('i');
                icon.className = likeBtn.classList.contains('liked') ? 'ph-fill ph-heart' : 'ph ph-heart';
                
                const span = likeBtn.querySelector('.like-count');
                let count = parseInt(span.textContent || '0');
                count = method === 'POST' ? count + 1 : count - 1;
                span.textContent = count > 0 ? count : '';
            }
        } catch (e) {
            console.error("Like failed");
        }
    });

    return div;
}

function setupComposePost() {
    const btn = document.getElementById('submit-post-btn');
    const textarea = document.getElementById('compose-textarea');
    
    if(!btn || !textarea) return;

    btn.addEventListener('click', async () => {
        const content = textarea.value.trim();
        if(!content) return;
        
        btn.disabled = true;
        btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i>';
        
        try {
            const res = await apiFetch('/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            
            if(res.ok) {
                const data = await res.json();
                textarea.value = '';
                // Prepend new post
                const container = document.getElementById('feed-container');
                if (container) {
                    const newPost = data.data || data;
                    const postEl = createPostElement(newPost);
                    // Remove "No posts yet" message if it's there
                    if(container.children.length === 1 && !container.children[0].classList.contains('post')) {
                        container.innerHTML = '';
                    }
                    container.prepend(postEl);
                }
            } else {
                alert("Failed to post tweet.");
            }
        } catch(e) {
            alert("Error posting.");
        } finally {
            btn.disabled = false;
            btn.textContent = 'Post';
        }
    });
}

// --- Profile ---

async function loadProfile() {
    const usernameInput = document.getElementById('viewed-username');
    if(!usernameInput) return;
    
    const username = usernameInput.value;
    
    try {
        const res = await apiFetch(`/users/username/${username}`);
        if(res.ok) {
            const data = await res.json();
            const user = data.data || data;
            
            document.getElementById('header-display-name').textContent = user.username;
            document.getElementById('profile-display-name').textContent = user.username;
            document.getElementById('profile-username').textContent = `@${user.username}`;
            
            if(user.bio) {
                document.getElementById('profile-bio').textContent = user.bio;
            }
            
            document.getElementById('profile-joined-date').textContent = new Date(user.created_at || Date.now()).toLocaleString('default', { month: 'long', year: 'numeric' });
            document.getElementById('profile-following-count').textContent = user.following_count || 0;
            document.getElementById('profile-followers-count').textContent = user.followers_count || 0;
            
            // Setup follow button if not current user
            const currentUser = JSON.parse(localStorage.getItem('user'));
            const actionsContainer = document.getElementById('profile-actions-container');
            if (currentUser && currentUser.username === user.username) {
                actionsContainer.innerHTML = '<button class="btn-secondary">Edit profile</button>';
            } else {
                const isFollowing = user.is_followed_by_current_user; // Assumes API returns this
                actionsContainer.innerHTML = `<button class="btn-secondary" id="follow-btn" data-userid="${user.id}">${isFollowing ? 'Following' : 'Follow'}</button>`;
                
                document.getElementById('follow-btn').addEventListener('click', async (e) => {
                    const btn = e.target;
                    const targetUserId = btn.getAttribute('data-userid');
                    const isFollowingNow = btn.textContent === 'Following';
                    const method = isFollowingNow ? 'DELETE' : 'POST';
                    
                    try {
                        const followRes = await apiFetch(`/follows/${targetUserId}`, { method });
                        if(followRes.ok) {
                            btn.textContent = isFollowingNow ? 'Follow' : 'Following';
                            // Adjust count locally
                            const countEl = document.getElementById('profile-followers-count');
                            let count = parseInt(countEl.textContent || '0');
                            countEl.textContent = isFollowingNow ? count - 1 : count + 1;
                        }
                    } catch (err) {
                        console.error(err);
                    }
                });
            }
            
            // Load user's posts
            loadUserPosts(user.id);
        } else {
            document.querySelector('.profile-hero').innerHTML = '<h2 style="padding:2rem;">User not found</h2>';
            document.getElementById('profile-feed-container').innerHTML = '';
        }
    } catch(e) {
        console.error(e);
    }
}

async function loadUserPosts(userId) {
    const container = document.getElementById('profile-feed-container');
    try {
        const res = await apiFetch(`/posts/user/${userId}`);
        const data = await res.json();
        
        container.innerHTML = '';
        const posts = (data.data ? data.data.posts : null) || data.posts || [];
        
        if (posts && posts.length > 0) {
            document.getElementById('header-post-count').textContent = `${posts.length} posts`;
            posts.forEach(post => {
                container.appendChild(createPostElement(post));
            });
        } else {
            document.getElementById('header-post-count').textContent = '0 posts';
            container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-secondary);">No posts yet.</div>';
        }
    } catch (e) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--error-color);">Failed to load posts.</div>';
    }
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
