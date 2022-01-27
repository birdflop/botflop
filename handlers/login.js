require('dotenv').config();
module.exports = client => {
	client.login(process.env.TOKEN);
	client.logger.info('Bot logged in');
};