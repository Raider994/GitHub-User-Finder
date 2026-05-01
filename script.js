let favorites = [];

// Загрузка избранных из localStorage при старте
window.onload = () => {
  const stored = localStorage.getItem('favorites');
  if (stored) {
    favorites = JSON.parse(stored);
    renderFavorites();
  }
};

// Обработка поиска
document.getElementById('searchBtn').addEventListener('click', () => {
  const username = document.getElementById('githubSearch').value.trim();
  if (username === '') {
    alert('Поле поиска не должно быть пустым!');
    return;
  }
  fetchUser(username);
});

function fetchUser(username) {
  fetch(`https://api.github.com/users/${username}`)
    .then(res => res.json())
    .then(user => {
      if (user.message === 'Not Found') {
        alert('Пользователь не найден');
        document.getElementById('results').innerHTML = '';
      } else {
        displayUser(user);
      }
    });
}

function displayUser(user) {
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = `
    <ul>
      <li>Имя: ${user.name || 'Нет данных'}</li>
      <li>Логин: ${user.login}</li>
      <li>Репозитории: ${user.public_repos}</li>
      <li><button onclick="addToFavorites('${user.login}', '${user.html_url}', '${user.avatar_url}', '${user.name}')">Добавить в избранное</button></li>
    </ul>
  `;
}

// Функция добавления в избранное
function addToFavorites(login, url, avatar, name) {
  if (!favorites.some(user => user.login === login)) {
    favorites.push({ login, url, avatar, name });
    saveFavorites();
    renderFavorites();
    alert('Пользователь добавлен в избранное');
  } else {
    alert('Этот пользователь уже в избранном');
  }
}

// Сохранение в localStorage
function saveFavorites() {
  localStorage.setItem('favorites', JSON.stringify(favorites));
}

// Отрисовка списка избранных
function renderFavorites() {
  const favoritesDiv = document.getElementById('favoritesList');
  favoritesDiv.innerHTML = '';

  if (favorites.length === 0) {
    favoritesDiv.innerHTML = '<p>Нет избранных пользователей</p>';
    return;
  }

  favorites.forEach(user => {
    favoritesDiv.innerHTML += `
      <div style="margin-bottom:15px;">
        <img src="${user.avatar}" width="50" height="50" style="vertical-align:middle; border-radius:50%;"/>
        <a href="${user.url}" target="_blank">${user.name} (${user.login})</a>
      </div>
    `;
  });
}