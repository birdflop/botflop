const fetch = (...args) => import('node-fetch').then(({ default: e }) => e(...args));
const { MessageEmbed } = require('discord.js');
const net = require('net');
// used https://github.com/FragLand/minestat/blob/master/JavaScript/minestat.js
const api_java = "https://api.mcsrvstat.us/2/";
const api_bedrock = "https://api.mcsrvstat.us/bedrock/2/";
const api_icon = "https://api.mcsrvstat.us/icon/";
module.exports = async function getServerStatus(message, client, address) {
    const ErrorEmbed = new MessageEmbed()
        .setColor('RED')
        .setTitle('Error!');
    const StatusEmbed = new MessageEmbed()
        .setColor('GREEN')
        .setTitle('Server Status');
    const dataJava = await fetch(api_java + address).then(res => res.json()).catch(err => ({ online: false }));
    const dataBedrock = await fetch(api_bedrock + address).then(res => res.json()).catch(err=> ({online: false}));
    if(dataJava['online'] == false && dataBedrock['online'] == false) return message.reply({ embeds: [ErrorEmbed.setDescription("The server is offline.") ]});

    if(dataJava['online'] == true) {
        StatusEmbed.addFields([
            {
                name: "Server Status",
                value: "Online",
                inline: true
            },
            {
                name: "Server Type",
                value: "Java",
                inline: true
            },
            {
                name: "Server Address",
                value: dataJava['ip'],
                inline: true
            },
            {
                name: "Server Online",
                value: dataJava['players']['online'] + "/" + dataJava['players']['max'],
                inline: true
            },
            {
                name: "Server Version",
                value: dataJava['version'],
                inline: true
            }
        ])
        StatusEmbed.setThumbnail(api_icon + address);
        return message.reply({ embeds: [StatusEmbed] });
    } else if(dataBedrock['online'] == true) {
        StatusEmbed.addFields([
            {
                name: "Server Status",
                value: "Online",
                inline: true
            },
            {
                name: "Server Type",
                value: "Bedrock",
                inline: true
            },
            {
                name: "Server Address",
                value: dataBedrock['ip'],
                inline: true
            },
            {
                name: "Server Online",
                value: dataBedrock['players']['online'] + "/" + dataBedrock['players']['max'],
                inline: true
            },
            {
                name: "Server Version",
                value: dataBedrock['version'],
                inline: true
            }
        ])
        StatusEmbed.setThumbnail(api_icon + address);
        return message.reply({ embeds: [StatusEmbed] });
    }
}