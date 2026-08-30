import re

with open('admin-frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

banner_html = """
                <!-- Admin Info Banner -->
                <div class="bg-blue-900/20 border border-blue-500/30 rounded-xl p-4 flex gap-4 items-start">
                    <div class="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                        <i class="fa-solid fa-circle-info text-xl"></i>
                    </div>
                    <div>
                        <h4 class="text-sm font-bold text-blue-300 mb-1">Hurmatli Admin!</h4>
                        <p class="text-xs text-slate-300 leading-relaxed">
                            Ushbu boshqaruv panelida siz Maklersiz.uz foydalanuvchilarining barcha ma'lumotlarini kuzatishingiz mumkin. "Foydalanuvchilar" bo'limida yangi ro'yxatdan o'tganlarning ism-sharifi, telefon raqami, qachon a'zo bo'lganligi va endilikda ularning maxfiy paroli ham keltirilgan. Parolni ko'rish uchun yashirin yozuv yonidagi "Ko'z" belgisini bosing. Mijozlarning parollarini uchinchi shaxslarga bermaslikni va xavfsizlikni ta'minlashni unutmang!
                        </p>
                    </div>
                </div>
"""

# Insert banner before USERS TABLE
content = content.replace("<!-- USERS TABLE -->", banner_html + "\n                <!-- USERS TABLE -->")

# Replace JS password render
old_pwd_render = """                        <td class="px-6 py-4 font-mono">
                            <span class="bg-slate-900 border border-slate-700/80 text-amber-300 font-bold px-2.5 py-1 rounded-lg text-xs tracking-wider inline-flex items-center gap-1.5" title="${pwd}">
                                <i class="fa-solid fa-key text-[10px] text-amber-400"></i>
                                <span>${pwd}</span>
                            </span>
                        </td>"""

new_pwd_render = """                        <td class="px-6 py-4 font-mono">
                            <div class="bg-slate-900 border border-slate-700/80 text-amber-300 font-bold px-2.5 py-1 rounded-lg text-xs tracking-wider inline-flex items-center gap-1.5 cursor-pointer select-none hover:bg-slate-800 transition" onclick="togglePwd(this, '${pwd}')" title="Parolni ko'rish/yashirish">
                                <i class="fa-solid fa-eye text-[10px] text-amber-400"></i>
                                <span>******</span>
                            </div>
                        </td>"""

content = content.replace(old_pwd_render, new_pwd_render)

# Add registration date to user info
old_user_info = """                                <div class="text-[11px] text-slate-400">${listingsCount} ta e'loni bor</div>"""
new_user_info = """                                <div class="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                                    <span>${listingsCount} ta e'lon</span>
                                    <span>•</span>
                                    <span class="text-slate-500"><i class="fa-regular fa-clock mr-1"></i>A'zo: ${regDate}</span>
                                </div>"""

# Insert regDate calculation before return `...
reg_date_calc = """
                    const listingsCount = u.listings_count !== undefined ? u.listings_count : (u.listingsCount !== undefined ? u.listingsCount : 0);
                    const isVerified = trustScore >= 90;
                    const verifiedBadgeHtml = isVerified 
                        ? `<span class="text-blue-400 text-xs ml-1" title="Tasdiqlangan Foydalanuvchi (Verified)"><i class="fa-solid fa-circle-check"></i></span>`
                        : '';
                        
                    const regDate = u.created_at ? new Date(u.created_at).toLocaleDateString('ru-RU') : (u.createdAt ? new Date(u.createdAt).toLocaleDateString('ru-RU') : 'Yaqinda');
"""

content = content.replace("""                    const listingsCount = u.listings_count !== undefined ? u.listings_count : (u.listingsCount !== undefined ? u.listingsCount : 0);
                    const isVerified = trustScore >= 90;
                    const verifiedBadgeHtml = isVerified 
                        ? `<span class="text-blue-400 text-xs ml-1" title="Tasdiqlangan Foydalanuvchi (Verified)"><i class="fa-solid fa-circle-check"></i></span>`
                        : '';""", reg_date_calc)
content = content.replace(old_user_info, new_user_info)

# Add the togglePwd function at the end of loadUsers block or globally
toggle_func = """
        function togglePwd(el, realPwd) {
            const span = el.querySelector('span');
            const icon = el.querySelector('i');
            if (span.textContent === '******') {
                span.textContent = realPwd;
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                span.textContent = '******';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }
"""
content = content.replace("async function grantUserVerification(userId) {", toggle_func + "\n        async function grantUserVerification(userId) {")

with open('admin-frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
