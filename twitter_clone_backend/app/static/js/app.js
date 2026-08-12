const API_BASE = '/api/v1';

// --- Utility Functions & Storage ---

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

// --- Toast Notification Banner ---
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-message ${type === 'error' ? 'toast-error' : type === 'success' ? 'toast-success' : ''}`;
    
    let iconClass = 'ph-check-circle';
    if (type === 'error') iconClass = 'ph-warning-circle';
    if (type === 'info') iconClass = 'ph-info';

    toast.innerHTML = `<i class="ph ${iconClass}"></i> <span>${escapeHTML(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --- Shimmer Skeleton Loader ---
function renderSkeletons(container, count = 3) {
    if (!container) return;
    let html = '';
    for (let i = 0; i < count; i++) {
        html += `
            <div class="skeleton-card">
                <div class="skeleton-avatar"></div>
                <div class="skeleton-content">
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line full"></div>
                    <div class="skeleton-line medium"></div>
                </div>
            </div>
        `;
    }
    container.innerHTML = html;
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
        removeToken();
        localStorage.removeItem('user');
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
        throw new Error('Unauthorized');
    }
    
    return response;
}

function formatTime(isoString) {
    if (!isoString) return 'Just now';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);

    if (diffSec < 15) return 'Just now';
    if (diffSec < 60) return `${diffSec}s`;
    if (diffMin < 60) return `${diffMin}m`;
    if (diffHour < 24) return `${diffHour}h`;
    if (diffDay < 7) return `${diffDay}d`;
    return `${date.toLocaleString('default', { month: 'short' })} ${date.getDate()}`;
}

// --- App Initialization ---

document.addEventListener('DOMContentLoaded', () => {
    // Check login page
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        setupAuthForms();
    }

    // Protected pages setup
    const token = getToken();
    const path = window.location.pathname;

    if (!token && path !== '/') {
        window.location.href = '/';
    } else if (token) {
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
                        setupFeedTabs();
                    } else if (path.length > 1 && path !== '/feed') {
                        loadProfile();
                    }
                }
            }).catch(() => {
                setupUserInterface();
                if (path === '/feed') {
                    loadFeed();
                    setupComposePost();
                    setupFeedTabs();
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

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailOrUsername = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;
            const errorDiv = document.getElementById('login-error');

            const payload = { email: emailOrUsername, username: emailOrUsername, password };

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                if (res.ok) {
                    setToken(data.data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.data.user));
                    showToast('Welcome back! Logging in...', 'success');
                    setTimeout(() => { window.location.href = '/feed'; }, 400);
                } else {
                    const msg = data.message === 'An unexpected server error occurred'
                        ? 'Incorrect email/username or password. Please try again.'
                        : (data.message || 'Login failed.');
                    errorDiv.textContent = msg;
                    errorDiv.classList.remove('hidden');
                    showToast(msg, 'error');
                }
            } catch (err) {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.classList.remove('hidden');
                showToast('Network error.', 'error');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('register-username').value.trim();
            const email = document.getElementById('register-email').value.trim();
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
                    showToast('Account created! Logging in...', 'success');
                    // Auto login after registration
                    const loginRes = await fetch(`${API_BASE}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    const loginData = await loginRes.json();
                    if (loginRes.ok) {
                        setToken(loginData.data.access_token);
                        localStorage.setItem('user', JSON.stringify(loginData.data.user));
                        setTimeout(() => { window.location.href = '/feed'; }, 400);
                    }
                } else {
                    const msg = data.message === 'An unexpected server error occurred'
                        ? 'Could not register account. Username or email may already be registered.'
                        : (data.message || 'Registration failed.');
                    errorDiv.textContent = msg;
                    errorDiv.classList.remove('hidden');
                    showToast(msg, 'error');
                }
            } catch (err) {
                errorDiv.textContent = 'Error creating account.';
                errorDiv.classList.remove('hidden');
                showToast('Error creating account.', 'error');
            }
        });
    }
}

function setupUserInterface() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            const miniProfile = document.getElementById('current-user-miniprofile');
            if (miniProfile) {
                miniProfile.style.display = 'flex';
                const displayNameEl = document.getElementById('current-user-display-name');
                const usernameEl = document.getElementById('current-user-username');
                if (displayNameEl) displayNameEl.textContent = user.username;
                if (usernameEl) usernameEl.textContent = `@${user.username}`;
                
                miniProfile.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const menu = document.getElementById('logout-menu');
                    if (menu) menu.classList.toggle('hidden');
                });

                document.addEventListener('click', () => {
                    const menu = document.getElementById('logout-menu');
                    if (menu && !menu.classList.contains('hidden')) {
                        menu.classList.add('hidden');
                    }
                });

                const logoutBtn = document.getElementById('logout-btn');
                if (logoutBtn) {
                    logoutBtn.addEventListener('click', () => {
                        removeToken();
                        localStorage.removeItem('user');
                        showToast('Logged out.', 'info');
                        setTimeout(() => { window.location.href = '/'; }, 300);
                    });
                }
                
                // Set profile nav link
                const profileLink = document.getElementById('nav-profile');
                const mobileProfileLink = document.getElementById('mobile-nav-profile');
                if (profileLink) profileLink.href = `/${user.username}`;
                if (mobileProfileLink) mobileProfileLink.href = `/${user.username}`;
            }
        } catch (e) {}
    }
}

// --- Feed & Posts ---

async function loadFeed() {
    const container = document.getElementById('feed-container');
    if (!container) return;
    
    renderSkeletons(container, 3);
    
    try {
        const res = await apiFetch('/feed');
        const data = await res.json();
        
        container.innerHTML = '';
        
        const posts = (data.data ? data.data.posts : null) || data.posts || [];
        if (posts && posts.length > 0) {
            posts.forEach(post => {
                container.appendChild(createPostElement(post));
            });
        } else {
            container.innerHTML = `
                <div style="padding: 3rem 1.5rem; text-align: center; color: var(--text-muted);">
                    <i class="ph ph-sparkle" style="font-size: 2.5rem; color: var(--brand-primary); margin-bottom: 0.5rem;"></i>
                    <h3 style="color: var(--text-primary); margin-bottom: 0.25rem;">Welcome to your Feed!</h3>
                    <p style="font-size: 0.9rem;">Share your first post using the box above or follow creators to populate your timeline.</p>
                </div>
            `;
        }
    } catch (err) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--error-color);">Failed to load feed. Refresh to try again.</div>';
    }
}

function setupFeedTabs() {
    const tabForYou = document.getElementById('tab-for-you');
    const tabFollowing = document.getElementById('tab-following');

    if (tabForYou && tabFollowing) {
        tabForYou.addEventListener('click', () => {
            tabForYou.classList.add('active');
            tabFollowing.classList.remove('active');
            loadFeed();
        });

        tabFollowing.addEventListener('click', () => {
            tabFollowing.classList.add('active');
            tabForYou.classList.remove('active');
            loadFeed();
        });
    }
}

function createPostElement(post) {
    const div = document.createElement('div');
    div.className = 'post';
    
    const username = (post.author && post.author.username) || (post.user && post.user.username) || 'unknown';
    const content = post.content || '';
    const likes = post.likes_count || 0;
    const comments = post.comments_count || 0;
    const isLiked = post.liked_by_me || post.is_liked_by_current_user || false;
    const postId = post.id || post.post_id;
    
    div.innerHTML = `
        <div class="avatar-placeholder" onclick="event.stopPropagation(); window.location.href='/${username}'"></div>
        <div class="post-content-container">
            <div class="post-header">
                <a href="/${username}" class="post-display-name" onclick="event.stopPropagation();">${escapeHTML(username)}</a>
                <span class="post-username">@${escapeHTML(username)}</span>
                <span class="post-time">· ${formatTime(post.created_at)}</span>
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
                <div class="post-action action-like ${isLiked ? 'liked' : ''}" data-id="${postId}">
                    <i class="${isLiked ? 'ph-fill ph-heart' : 'ph ph-heart'}"></i>
                    <span class="like-count">${likes > 0 ? likes : ''}</span>
                </div>
                <div class="post-action action-share" data-id="${postId}" title="Share post">
                    <i class="ph ph-export"></i>
                </div>
            </div>
        </div>
    `;
    
    // Action Listeners
    const likeBtn = div.querySelector('.action-like');
    if (likeBtn) {
        likeBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const targetPostId = likeBtn.getAttribute('data-id');
            const isCurrentlyLiked = likeBtn.classList.contains('liked');
            const method = isCurrentlyLiked ? 'DELETE' : 'POST';
            
            // Optimistic UI update
            likeBtn.classList.toggle('liked');
            const icon = likeBtn.querySelector('i');
            icon.className = !isCurrentlyLiked ? 'ph-fill ph-heart' : 'ph ph-heart';
            const span = likeBtn.querySelector('.like-count');
            let count = parseInt(span.textContent || '0');
            count = !isCurrentlyLiked ? count + 1 : count - 1;
            span.textContent = count > 0 ? count : '';

            try {
                const res = await apiFetch(`/posts/${targetPostId}/like`, { method });
                if (!res.ok) {
                    // Revert if API fails
                    likeBtn.classList.toggle('liked');
                    icon.className = isCurrentlyLiked ? 'ph-fill ph-heart' : 'ph ph-heart';
                    span.textContent = likes > 0 ? likes : '';
                    showToast('Failed to update like.', 'error');
                }
            } catch (e) {
                console.error("Like request error", e);
            }
        });
    }

    const shareBtn = div.querySelector('.action-share');
    if (shareBtn) {
        shareBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const postUrl = `${window.location.origin}/${username}`;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(postUrl);
                showToast('Link copied to clipboard! ✨', 'info');
            } else {
                showToast('Post link copied!', 'info');
            }
        });
    }

    return div;
}

// --- Compose Post & Character Limit ---

function setupComposePost() {
    const desktopTextarea = document.getElementById('compose-textarea');
    const desktopBtn = document.getElementById('submit-post-btn');
    const desktopCounter = document.getElementById('desktop-char-counter');

    if (desktopTextarea) {
        bindCharCounter(desktopTextarea, desktopCounter, desktopBtn);
    }
    if (desktopBtn && desktopTextarea) {
        desktopBtn.addEventListener('click', () => submitPost(desktopTextarea, desktopBtn));
    }

    // Mobile FAB + Bottom Sheet Modal
    const fab = document.getElementById('mobile-compose-fab');
    const modal = document.getElementById('mobile-compose-modal');
    const closeBtn = document.getElementById('mobile-compose-close');
    const mobileTextarea = document.getElementById('mobile-compose-textarea');
    const mobileSubmitBtn = document.getElementById('mobile-submit-post-btn');
    const mobileCounter = document.getElementById('mobile-char-counter');

    if (mobileTextarea) {
        bindCharCounter(mobileTextarea, mobileCounter, mobileSubmitBtn);
    }

    if (fab && modal) {
        fab.addEventListener('click', () => {
            modal.classList.add('open');
            setTimeout(() => mobileTextarea && mobileTextarea.focus(), 100);
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => modal.classList.remove('open'));
        }

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('open');
        });

        if (mobileSubmitBtn && mobileTextarea) {
            mobileSubmitBtn.addEventListener('click', async () => {
                await submitPost(mobileTextarea, mobileSubmitBtn);
                modal.classList.remove('open');
            });
        }
    }
}

function bindCharCounter(textarea, counterEl, submitBtn) {
    const MAX = 280;
    textarea.addEventListener('input', () => {
        const len = textarea.value.length;
        if (counterEl) {
            counterEl.textContent = `${len}/${MAX}`;
            counterEl.className = 'char-counter';
            if (len >= 240 && len <= MAX) counterEl.classList.add('warning');
            if (len > MAX) counterEl.classList.add('exceeded');
        }
        if (submitBtn) {
            submitBtn.disabled = len === 0 || len > MAX;
        }
    });
}

async function submitPost(textarea, btn) {
    const content = textarea.value.trim();
    if (!content || content.length > 280) return;

    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i>';

    try {
        const res = await apiFetch('/posts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });

        if (res.ok) {
            const data = await res.json();
            textarea.value = '';
            showToast('Post published! ✨', 'success');

            const container = document.getElementById('feed-container');
            if (container) {
                const newPost = data.data || data;
                const postEl = createPostElement(newPost);
                if (container.children.length === 1 && !container.children[0].classList.contains('post')) {
                    container.innerHTML = '';
                }
                container.prepend(postEl);
            }
        } else {
            showToast('Failed to publish post.', 'error');
        }
    } catch (e) {
        showToast('Error posting. Please check your connection.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// --- Profile ---

async function loadProfile() {
    const usernameInput = document.getElementById('viewed-username');
    if (!usernameInput) return;
    
    const username = usernameInput.value;
    const feedContainer = document.getElementById('profile-feed-container');
    renderSkeletons(feedContainer, 2);

    try {
        const res = await apiFetch(`/users/username/${username}`);
        if (res.ok) {
            const data = await res.json();
            const user = data.data || data;
            
            const headerName = document.getElementById('header-display-name');
            const profileName = document.getElementById('profile-display-name');
            const profileHandle = document.getElementById('profile-username');
            const profileBio = document.getElementById('profile-bio');
            const joinedDate = document.getElementById('profile-joined-date');
            const followingCount = document.getElementById('profile-following-count');
            const followersCount = document.getElementById('profile-followers-count');

            if (headerName) headerName.textContent = user.username;
            if (profileName) profileName.textContent = user.username;
            if (profileHandle) profileHandle.textContent = `@${user.username}`;
            if (profileBio) profileBio.textContent = user.bio || 'No bio available.';
            if (joinedDate) joinedDate.textContent = new Date(user.created_at || Date.now()).toLocaleString('default', { month: 'long', year: 'numeric' });
            if (followingCount) followingCount.textContent = user.following_count || 0;
            if (followersCount) followersCount.textContent = user.followers_count || 0;
            
            // Follow button setup
            const currentUser = JSON.parse(localStorage.getItem('user'));
            const actionsContainer = document.getElementById('profile-actions-container');
            if (actionsContainer) {
                if (currentUser && currentUser.username === user.username) {
                    actionsContainer.innerHTML = '<button class="btn-secondary">Edit profile</button>';
                } else {
                    const isFollowing = user.is_followed_by_current_user;
                    actionsContainer.innerHTML = `<button class="btn-secondary" id="follow-btn" data-userid="${user.id}">${isFollowing ? 'Following' : 'Follow'}</button>`;
                    
                    const followBtn = document.getElementById('follow-btn');
                    if (followBtn) {
                        followBtn.addEventListener('click', async () => {
                            const targetUserId = followBtn.getAttribute('data-userid');
                            const isFollowingNow = followBtn.textContent === 'Following';
                            const method = isFollowingNow ? 'DELETE' : 'POST';
                            
                            try {
                                const followRes = await apiFetch(`/follows/${targetUserId}`, { method });
                                if (followRes.ok) {
                                    followBtn.textContent = isFollowingNow ? 'Follow' : 'Following';
                                    showToast(isFollowingNow ? `Unfollowed @${user.username}` : `Following @${user.username}!`, 'info');
                                    const countEl = document.getElementById('profile-followers-count');
                                    if (countEl) {
                                        let count = parseInt(countEl.textContent || '0');
                                        countEl.textContent = isFollowingNow ? Math.max(0, count - 1) : count + 1;
                                    }
                                }
                            } catch (err) {
                                showToast('Follow request failed.', 'error');
                            }
                        });
                    }
                }
            }
            
            // Load user's posts
            loadUserPosts(user.id);
        } else {
            const profileHero = document.querySelector('.profile-hero');
            if (profileHero) profileHero.innerHTML = '<h2 style="padding: 2rem; text-align: center; color: var(--text-muted);">User profile not found.</h2>';
            if (feedContainer) feedContainer.innerHTML = '';
        }
    } catch (e) {
        console.error(e);
    }
}

async function loadUserPosts(userId) {
    const container = document.getElementById('profile-feed-container');
    try {
        const res = await apiFetch(`/posts/user/${userId}`);
        const data = await res.json();
        
        if (container) container.innerHTML = '';
        const posts = (data.data ? data.data.posts : null) || data.posts || [];
        const headerCount = document.getElementById('header-post-count');
        
        if (posts && posts.length > 0) {
            if (headerCount) headerCount.textContent = `${posts.length} ${posts.length === 1 ? 'post' : 'posts'}`;
            posts.forEach(post => {
                if (container) container.appendChild(createPostElement(post));
            });
        } else {
            if (headerCount) headerCount.textContent = '0 posts';
            if (container) {
                container.innerHTML = '<div style="padding: 3rem 1.5rem; text-align: center; color: var(--text-muted);">No posts yet.</div>';
            }
        }
    } catch (e) {
        if (container) {
            container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--error-color);">Failed to load user posts.</div>';
        }
    }
}

function escapeHTML(str) {
    if (!str) return '';
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
