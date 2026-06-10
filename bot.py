const
mineflayer = require('mineflayer');
const
{pathfinder, Movements, goals} = require('mineflayer-pathfinder');
const
config = require('./config.json');

// ─── Проверка
конфига ─────────────────────────────────────────────────────────
if (!config.owner | | config.owner == = 'ТвойНик') {
console.error('[ОШИБКА] Укажи свой ник в config.json в поле "owner"!');
process.exit(1);
}

console.log(`[INFO]
Владелец
бота: ${config.owner}
`);
console.log(`[INFO]
Подключаемся
к ${config.host}:${config.port}...
`);

// ─── Создание
бота ────────────────────────────────────────────────────────────
const
bot = mineflayer.createBot({
    host: config.host,
    port: config.port,
    username: config.username,
    version: config.version | | false,
});

bot.loadPlugin(pathfinder);

// ─── События ──────────────────────────────────────────────────────────────────
bot.once('spawn', () = > {
    console.log(`[✓] Бот
"${bot.username}"
зашёл
на
сервер!`);
console.log(`[INFO]
Слушаю
команды
только
от: ${config.owner}
`);
const
defaultMove = new
Movements(bot);
bot.pathfinder.setMovements(defaultMove);
});

bot.on('chat', (username, message) = > {
                                       // Игнорируем
собственные
сообщения
if (username === bot.username)
return;

// Логируем
весь
чат
console.log(`[ЧАТ] ${username}: ${message}
`);

// Слушаем
команды
ТОЛЬКО
от
владельца
if (username !== config.owner) return;

handleCommand(message);
});

bot.on('error', (err) = > console.error('[ОШИБКА]', err.message));
bot.on('kicked', (reason) = > console.error('[КИКНУТ]', reason));
bot.on('end', () = > {
console.log('[!] Соединение закрыто.');
process.exit(0);
});

// ─── Обработка
команд ─────────────────────────────────────────────────────────
function
handleCommand(message)
{
    const
args = message.trim().split(' ');
const
cmd = args[0].toLowerCase();

switch(cmd)
{

// !help
case
'!help':
bot.chat('Команды: !help, !come, !goto <x> <y> <z>, !follow <ник>, !stop, !dig, !pos, !say <текст>');
break;

// !come — подойти
к
владельцу
case
'!come': {
    const
player = bot.players[config.owner];
if (!player | | !player.entity)
{
    bot.chat('Не вижу тебя рядом!');
break;
}
const
{x, y, z} = player.entity.position;
bot.pathfinder.setGoal(new
goals.GoalNear(x, y, z, 2));
bot.chat('Иду к тебе!');
break;
}

// !goto < x > < y > < z >
    case
'!goto': {
const
x = parseFloat(args[1]);
const
y = parseFloat(args[2]);
const
z = parseFloat(args[3]);
if (isNaN(x) | | isNaN(y) | | isNaN(z)) {
bot.chat('Использование: !goto <x> <y> <z>');
break;
}
bot.pathfinder.setGoal(new
goals.GoalBlock(x, y, z));
bot.chat(`Иду
к(${x}, ${y}, ${z})`);
break;
}

// !follow < ник > (по умолчанию — владелец)
case
'!follow': {
const
targetName = args[1] | | config.owner;
const
player = bot.players[targetName];
if (!player | | !player.entity) {
bot.chat(`Не вижу игрока ${targetName} рядом.`);
break;
}
bot.pathfinder.setGoal(new
goals.GoalFollow(player.entity, 3), true);
bot.chat(`Следую
за ${targetName}!`);
break;
}

// !stop
case
'!stop': \
    bot.pathfinder.setGoal(null);
bot.chat('Остановился.');
break;

// !dig — копать
блок
перед
собой
case
'!dig': {
    const
targetBlock = bot.blockAtCursor(4);
if (!targetBlock)
{
    bot.chat('Нет блока перед собой.');
break;
}
bot.dig(targetBlock)
.then(() = > bot.chat('Готово!'))
.catch(() = > bot.chat('Не могу копать этот блок.'));
break;
}

// !pos — текущая
позиция
case
'!pos': {
const
{x, y, z} = bot.entity.position;
bot.chat(`Я
на: ${Math.floor(x)}, ${Math.floor(y)}, ${Math.floor(z)}
`);
break;
}

// !say < текст >
    case
'!say':
if (args.length < 2) {
bot.chat('Использование: !say <текст>');
break;
}
bot.chat(args.slice(1).join(' '));
break;

default:
// Неизвестная
команда — молча
игнорируем
break;
}
}