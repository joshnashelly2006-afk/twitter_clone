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
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        setupAuthForms();
    }

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
                    setupNavigation();
                    setupSearch();
                    loadRightSidebarData();

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
                setupNavigation();
                setupSearch();
                loadRightSidebarData();

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

// --- Navigation & Views ---

function setupNavigation() {
    const navExplore = document.getElementById('nav-explore');
    const navNotifications = document.getElementById('nav-notifications');
    const navHome = document.getElementById('nav-home');
    const mobileNavExplore = document.getElementById('mobile-nav-explore');
    const mobileNavNotifs = document.getElementById('mobile-nav-notifications');

    if (navExplore) {
        navExplore.addEventListener('click', (e) => {
            e.preventDefault();
            setActiveNav(navExplore);
            loadExplore();
        });
    }

    if (mobileNavExplore) {
        mobileNavExplore.addEventListener('click', (e) => {
            e.preventDefault();
            loadExplore();
        });
    }

    if (navNotifications) {
        navNotifications.addEventListener('click', (e) => {
            e.preventDefault();
            setActiveNav(navNotifications);
            loadNotifications();
        });
    }

    if (mobileNavNotifs) {
        mobileNavNotifs.addEventListener('click', (e) => {
            e.preventDefault();
            loadNotifications();
        });
    }
}

function setActiveNav(targetEl) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if (targetEl) targetEl.classList.add('active');
}

// --- Auth Forms ---

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
    
    const likeBtn = div.querySelector('.action-like');
    if (likeBtn) {
        likeBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const targetPostId = likeBtn.getAttribute('data-id');
            const isCurrentlyLiked = likeBtn.classList.contains('liked');
            const method = isCurrentlyLiked ? 'DELETE' : 'POST';
            
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

// --- Follow & Right Sidebar Data ---

async function toggleFollow(userId, btnElement, username = '') {
    if (!userId || !btnElement) return;

    const isFollowing = btnElement.classList.contains('following') || btnElement.textContent.trim() === 'Following';
    const method = isFollowing ? 'DELETE' : 'POST';

    // Optimistic state
    btnElement.textContent = isFollowing ? 'Follow' : 'Following';
    btnElement.classList.toggle('following');

    try {
        const res = await apiFetch(`/users/${userId}/follow`, { method });
        if (res.ok) {
            const label = username ? `@${username}` : 'user';
            showToast(isFollowing ? `Unfollowed ${label}` : `Following ${label}! ✨`, 'info');
        } else {
            // Revert
            btnElement.textContent = isFollowing ? 'Following' : 'Follow';
            btnElement.classList.toggle('following');
            showToast('Follow request failed.', 'error');
        }
    } catch (e) {
        btnElement.textContent = isFollowing ? 'Following' : 'Follow';
        btnElement.classList.toggle('following');
        showToast('Error sending follow request.', 'error');
    }
}

async function loadRightSidebarData() {
    const suggestionsContainer = document.getElementById('suggestions-container');
    if (suggestionsContainer) {
        try {
            const res = await apiFetch('/trending/users?limit=5');
            if (res.ok) {
                const data = await res.json();
                const users = data.data || [];
                const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

                const filtered = users.filter(u => u.username !== currentUser.username);
                if (filtered.length > 0) {
                    suggestionsContainer.innerHTML = '';
                    filtered.forEach(u => {
                        const card = document.createElement('div');
                        card.className = 'suggestion-user-card';
                        card.innerHTML = `
                            <div class="suggestion-user-info" onclick="window.location.href='/${u.username}'" style="cursor:pointer;">
                                <div class="avatar-placeholder" style="width:36px;height:36px;"></div>
                                <div>
                                    <div class="display-name" style="font-size:0.9rem;">${escapeHTML(u.username)}</div>
                                    <div class="handle" style="font-size:0.8rem;">@${escapeHTML(u.username)}</div>
                                </div>
                            </div>
                            <button class="follow-btn-sm" data-id="${u.id}" data-username="${u.username}">Follow</button>
                        `;
                        const fBtn = card.querySelector('.follow-btn-sm');
                        fBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            toggleFollow(u.id, fBtn, u.username);
                        });
                        suggestionsContainer.appendChild(card);
                    });
                }
            }
        } catch (e) {}
    }
}

// --- Live Search ---

function setupSearch() {
    const input = document.getElementById('global-search-input');
    if (!input) return;

    let debounceTimeout = null;

    input.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        const query = input.value.trim();
        if (!query) return;

        debounceTimeout = setTimeout(() => {
            performGlobalSearch(query);
        }, 300);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = input.value.trim();
            if (query) performGlobalSearch(query);
        }
    });
}

async function performGlobalSearch(query) {
    const feedContainer = document.getElementById('feed-container');
    if (feedContainer) {
        renderSkeletons(feedContainer, 2);
    }

    try {
        const res = await apiFetch(`/search?q=${encodeURIComponent(query)}`);
        if (res.ok) {
            const data = await res.json();
            const results = data.data || {};
            
            if (feedContainer) {
                feedContainer.innerHTML = `
                    <div style="padding: 1rem 1.25rem; border-bottom: 1px solid var(--border-color);">
                        <h3 style="font-size: 1.1rem;">Search results for "${escapeHTML(query)}"</h3>
                    </div>
                `;

                // Render User Results
                if (results.users && results.users.length > 0) {
                    results.users.forEach(u => {
                        const uEl = document.createElement('div');
                        uEl.className = 'suggestion-user-card';
                        uEl.style.padding = '1rem 1.25rem';
                        uEl.style.borderBottom = '1px solid var(--border-color)';
                        uEl.innerHTML = `
                            <div class="suggestion-user-info" onclick="window.location.href='/${u.username}'" style="cursor:pointer;">
                                <div class="avatar-placeholder" style="width:44px;height:44px;"></div>
                                <div>
                                    <div class="display-name" style="font-size:0.95rem; font-weight:700;">${escapeHTML(u.username)}</div>
                                    <div class="handle" style="font-size:0.85rem;">@${escapeHTML(u.username)}</div>
                                    <div style="font-size:0.85rem; color:var(--text-muted); margin-top:2px;">${escapeHTML(u.bio || '')}</div>
                                </div>
                            </div>
                            <button class="follow-btn-sm" data-id="${u.id}" data-username="${u.username}">Follow</button>
                        `;
                        const fBtn = uEl.querySelector('.follow-btn-sm');
                        fBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            toggleFollow(u.id, fBtn, u.username);
                        });
                        feedContainer.appendChild(uEl);
                    });
                }

                // Render Post Results
                if (results.posts && results.posts.length > 0) {
                    results.posts.forEach(post => {
                        feedContainer.appendChild(createPostElement(post));
                    });
                }

                if ((!results.users || results.users.length === 0) && (!results.posts || results.posts.length === 0)) {
                    feedContainer.innerHTML += `
                        <div style="padding: 3rem 1.5rem; text-align: center; color: var(--text-muted);">
                            No results found for "${escapeHTML(query)}".
                        </div>
                    `;
                }
            }
            showToast(`Found search results for "${query}"`, 'info');
        }
    } catch (e) {
        showToast('Search failed.', 'error');
    }
}

// --- Notifications View ---

async function loadNotifications() {
    const container = document.getElementById('feed-container');
    if (!container) return;

    renderSkeletons(container, 3);

    try {
        const res = await apiFetch('/notifications');
        if (res.ok) {
            const data = await res.json();
            const notifs = (data.data ? data.data.notifications : null) || data.notifications || [];
            
            container.innerHTML = `
                <div style="padding: 1rem 1.25rem; border-bottom: 1px solid var(--border-color);">
                    <h3 style="font-size: 1.15rem; font-weight: 800;">Notifications</h3>
                </div>
            `;

            if (notifs && notifs.length > 0) {
                notifs.forEach(n => {
                    const el = document.createElement('div');
                    el.className = 'post';
                    const sender = n.sender ? n.sender.username : 'Someone';
                    let icon = 'ph-bell';
                    let text = 'interacted with your profile';
                    if (n.type === 'LIKE') { icon = 'ph-heart'; text = 'liked your post'; }
                    if (n.type === 'FOLLOW') { icon = 'ph-user-plus'; text = 'started following you'; }
                    if (n.type === 'COMMENT') { icon = 'ph-chat-circle'; text = 'commented on your post'; }
                    if (n.type === 'MENTION') { icon = 'ph-at'; text = 'mentioned you in a post'; }

                    el.innerHTML = `
                        <div style="font-size: 1.5rem; color: var(--brand-primary); padding-top:4px;">
                            <i class="ph ${icon}"></i>
                        </div>
                        <div class="post-content-container">
                            <div class="post-header">
                                <strong class="post-display-name">${escapeHTML(sender)}</strong>
                                <span class="post-time">· ${formatTime(n.created_at)}</span>
                            </div>
                            <div class="post-text">${escapeHTML(text)}</div>
                        </div>
                    `;
                    container.appendChild(el);
                });
            } else {
                container.innerHTML += `
                    <div style="padding: 3rem 1.5rem; text-align: center; color: var(--text-muted);">
                        <i class="ph ph-bell-slash" style="font-size: 2.5rem; color: var(--brand-primary); margin-bottom: 0.5rem;"></i>
                        <h3 style="color: var(--text-primary);">No notifications yet</h3>
                        <p style="font-size: 0.9rem;">When people like, comment, or follow you, you'll see it here.</p>
                    </div>
                `;
            }
        }
    } catch (e) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--error-color);">Failed to load notifications.</div>';
    }
}

// --- Explore View ---

async function loadExplore() {
    const container = document.getElementById('feed-container');
    if (!container) return;

    renderSkeletons(container, 3);

    try {
        const res = await apiFetch('/trending/posts');
        if (res.ok) {
            const data = await res.json();
            const posts = data.data || [];
            
            container.innerHTML = `
                <div style="padding: 1rem 1.25rem; border-bottom: 1px solid var(--border-color);">
                    <h3 style="font-size: 1.15rem; font-weight: 800;">Explore & Trending</h3>
                </div>
            `;

            if (posts && posts.length > 0) {
                posts.forEach(post => container.appendChild(createPostElement(post)));
            } else {
                container.innerHTML += '<div style="padding: 3rem 1.5rem; text-align: center; color: var(--text-muted);">No trending posts right now.</div>';
            }
        }
    } catch (e) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--error-color);">Failed to load explore feed.</div>';
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
            
            const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
            const actionsContainer = document.getElementById('profile-actions-container');
            if (actionsContainer) {
                if (currentUser && currentUser.username === user.username) {
                    actionsContainer.innerHTML = '<button class="btn-secondary">Edit profile</button>';
                } else {
                    const isFollowing = user.is_followed_by_current_user;
                    actionsContainer.innerHTML = `<button class="btn-secondary ${isFollowing ? 'following' : ''}" id="follow-btn" data-userid="${user.id}">${isFollowing ? 'Following' : 'Follow'}</button>`;
                    
                    const followBtn = document.getElementById('follow-btn');
                    if (followBtn) {
                        followBtn.addEventListener('click', () => {
                            toggleFollow(user.id, followBtn, user.username);
                        });
                    }
                }
            }
            
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
