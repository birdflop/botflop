const analyzeTimings = require('../functions/analyzeTimings');
module.exports = async (client, message) => {
	if (message.author.bot) return;
	const timings = await analyzeTimings(message, client, message.content.split(' '));
	if (timings) await message.reply(timings);
};