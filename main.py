import os
from datetime import datetime

import discord
import matplotlib.pyplot as plt
import requests
from discord import ui, SelectOption
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

from bot_token import token

""" Cria uma conexão com a API da CoinGecko 
que é uma plataforma que fornece informações detalhadas sobre criptomoedas."""
cg = CoinGeckoAPI()

intents = discord.Intents.default()
intents.message_content = True

""" Sem esse parâmetro "help_command=None" o comando help versão EN não funciona,
 porquê o comando help é padrão discord.py aí da conflito."""
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)


# Evento para iniciar o Bot.
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} ON!")


@bot.command(name="hora")
async def hora_comando(ctx):
    hora_atual = datetime.now().strftime("%H:%M")
    await ctx.send(f"Agora são {hora_atual}!")


@bot.tree.command(name="hora", description="Mostra a hora atual")
async def hora_slash(interaction: discord.Interaction):
    hora_atual = datetime.now().strftime("%H:%M")
    await interaction.response.send_message(f"Agora são {hora_atual}!")


@bot.command(name="time")
async def time_command(ctx):
    current_time = datetime.now().strftime("%I:%M %p")
    await ctx.send(f"The current time is {current_time}!")


@bot.tree.command(name="time")
async def time_slash(interaction: discord.Interaction):
    current_time = datetime.now().strftime("%I:%M %p")
    await interaction.response.send_message(f"The current time is {current_time}!")


# Sistema de menu do comando "ajuda".
class HelpDropdown(ui.Select):
    def __init__(self):

        options = [SelectOption(label="General", description="Comandos gerais do bot."),
                   SelectOption(label="Crypto", description="Comandos relacionados a criptomoedas."), ]
        super().__init__(placeholder="Escolha uma categoria...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "General":
            embed = discord.Embed(title="Comandos: General", description="`hora`, `ajuda`", color=0x0B5394)
        elif self.values[0] == "Crypto":
            embed = discord.Embed(title="Comandos: Crypto",
                                  description="`preco`, `variacao`, `fandg`, `volume`, `grafico`", color=0x0B5394)

        await interaction.response.edit_message(embed=embed)


# Essa classe cria e gerencia a interface interativa do comando "ajuda".
class HelpView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())


@bot.command(name="ajuda")
async def ajuda_comando(ctx):
    embed = discord.Embed(title="Comandos: ", description="*Todos os comandos do Bot.*", color=0x0B5394)
    embed.add_field(name="**Básicos**", value="`hora`, `ajuda`", inline=False)
    embed.add_field(name="**Crypto**", value="`preco`, `variacao`, `fandg`, `volume`, `grafico`", inline=False)
    embed.set_footer(text="Selecione uma categoria abaixo para mais detalhes.")

    await ctx.send(embed=embed, view=HelpView())


@bot.tree.command(name="ajuda", description="Mostra todos os comandos do Bot.")
async def ajuda_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Comandos: ", description="*Todos os comandos do Bot.*", color=0x0B5394)
    embed.add_field(name="**Básicos**", value="`hora`, `ajuda`", inline=False)
    embed.add_field(name="**Crypto**", value="`preco`, `variacao`, `fandg`, `volume`, `grafico`", inline=False)
    embed.set_footer(text="Selecione uma categoria abaixo para mais detalhes.")

    await interaction.response.send_message(embed=embed, view=HelpView())


# Mesma coisa do de cima mas para o comando versão inglês.
class HelpDropdownEn(ui.Select):
    def __init__(self):
        options = [SelectOption(label="General", description="General bot commands."),
                   SelectOption(label="Crypto", description="Cryptocurrency-related commands."), ]
        super().__init__(placeholder="Choose a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "General":
            embed = discord.Embed(title="Commands: General", description="`time`, `help`", color=0x0B5394)
        elif self.values[0] == "Crypto":
            embed = discord.Embed(title="Commands: Crypto",
                                  description="`price`, `variation`, `fandg`, `volume`, `chart`", color=0x0B5394)

        await interaction.response.edit_message(embed=embed)


class HelpViewEn(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdownEn())


@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Commands: ", description="*All Bot commands.*", color=0x0B5394)
    embed.add_field(name="**General**", value="`time`, `help`", inline=False)
    embed.add_field(name="**Crypto**", value="`price`, `variation`, `fandg`, `volume`, `chart`", inline=False)
    embed.set_footer(text="Select a category below for more details.")

    await ctx.send(embed=embed, view=HelpViewEn())


@bot.tree.command(name="help", description="Shows all Bot commands.")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands: ", description="*All Bot commands.*", color=0x0B5394)
    embed.add_field(name="**General**", value="`time`, `help`", inline=False)
    embed.add_field(name="**Crypto**", value="`price`, `variation`, `fandg`, `volume`, `chart`", inline=False)
    embed.set_footer(text="Select a category below for more details.")

    await interaction.response.send_message(embed=embed, view=HelpViewEn())


# "moeda" é a criptomoeda que vai ser consultada e "moeda_ref" é em qual moeda eu desejo saber o preço. Ex: Real, Euro
@bot.command(name="preco")
async def preco(ctx, moeda: str):
    await buscar_preco(ctx, moeda, "pt", "brl")


@bot.command(name="price")
async def price(ctx, moeda: str):
    await buscar_preco(ctx, moeda, "en", "usd")


async def buscar_preco(ctx, moeda: str, idioma: str, moeda_ref: str):
    moeda = moeda.lower()
    mensagens = {
        "pt": {"erro_busca": "Desculpe, não consegui encontrar essa criptomoeda.", "preco_atual": "O preço atual de",
               "erro_preco": "Desculpe, não consegui encontrar o preço dessa criptomoeda.",
               "erro_geral": "Erro ao buscar o preço:"},
        "en": {"erro_busca": "Sorry, I couldn't find this cryptocurrency.", "preco_atual": "The current price of",
               "erro_preco": "Sorry, I couldn't find the price of this cryptocurrency.",
               "erro_geral": "Error fetching the price:"}}


""" A função do "try" em 90% do código é proteger o código contra erros
     caso ele não consiga encontrar a criptomoeda por algum motivo que seja."""
try:
    resultado_busca = cg.search(moeda)
    if not resultado_busca['coins']:
        await ctx.send(mensagens[idioma]["erro_busca"])
        return

    id_cripto = resultado_busca['coins'][0]['id']
    preco = cg.get_price(ids=id_cripto, vs_currencies=moeda_ref)

    if preco and id_cripto in preco:
        preco_formatado = f"{preco[id_cripto][moeda_ref]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        await ctx.send(
            f"**{mensagens[idioma]['preco_atual']} {moeda.upper()} é {preco_formatado} {moeda_ref.upper()}!**")
    else:
        await ctx.send(mensagens[idioma]["erro_preco"])

except Exception as e:
    await ctx.send(f"{mensagens[idioma]['erro_geral']} {str(e)}")


@bot.tree.command(name="preco", description="Mostra o preço de uma criptomoeda em reais.")
async def preco_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        preco = cg.get_price(ids=id_cripto, vs_currencies='brl')

        if preco and id_cripto in preco:
            preco_formatado = f"{preco[id_cripto]['brl']:,}".replace(',', '.') + ' BRL'
            await interaction.response.send_message(f"**O preço atual de {moeda.upper()} é {preco_formatado}!**")
        else:
            await interaction.response.send_message("Desculpe, não consegui encontrar o preço dessa criptomoeda.")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar o preço: {str(e)}")


@bot.tree.command(name="price")
async def price_slash(interaction: discord.Interaction, coin: str):
    try:
        coin = coin.lower()
        resultado_busca = cg.search(coin)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Sorry, I couldn't find this cryptocurrency.")
            return

        id_cripto = resultado_busca['coins'][0]['id']
        preco = cg.get_price(ids=id_cripto, vs_currencies='usd')

        if preco and id_cripto in preco:
            preco_formatado = f"${preco[id_cripto]['usd']:,}".replace(',', '.')
            await interaction.response.send_message(f"**The current price of {coin.upper()} is {preco_formatado}!**")
        else:
            await interaction.response.send_message("Sorry, I couldn't retrieve the price of this cryptocurrency.")
    except Exception as e:
        await interaction.response.send_message(f"Error fetching the price: {str(e)}")


# Extraindo dados da API CoinGecko para os comandos do Bot.
btc_url = "https://api.coingecko.com/api/v3/coins/bitcoin"
response = requests.get(btc_url)
fandg_btc_url = "https://api.alternative.me/fng/?limit=1"
response_fandg = requests.get(fandg_btc_url)

# Garantir que o Bot só tente acessar os dados caso a resposta da API seja válida, para evitar erros.
if response_fandg.status_code == 200:
    data_fandg = response_fandg.json()
    fandg_btc_ = data_fandg['data'][0]['value']
    descricao_fandgbtc = data_fandg['data'][0]['value_classification']
else:
    fandg_btc_ = "N/A"
    descricao_fandgbtc = "N/A"

data = response.json()
data_fandg = response_fandg.json()
btc_variacao_24h = data['market_data']['price_change_percentage_24h']
fandg_btc_ = data_fandg['data'][0]['value']
descricao_fandgbtc = data_fandg['data'][0]['value_classification']
btc_dados = cg.get_price(ids='bitcoin', vs_currencies='brl')


# Fim da extração

# Comandos para saber a variação do preço das criptomoedas em 24h nos dois idiomas PT-BR/EN.
@bot.command(name="variacao")
async def variacao(ctx, moeda: str):
    await fetch_variacao(ctx, moeda, "pt")


@bot.command(name="variation")
async def variation(ctx, moeda: str):
    await fetch_variacao(ctx, moeda, "en")


# Essa função é para buscar e retornar a variação do preço.
async def fetch_variacao(ctx, moeda, lang):
    moeda = moeda.lower()

    try:
        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            msg = "Desculpe, não consegui encontrar essa criptomoeda." if lang == "pt" else "Sorry, I couldn't find this cryptocurrency."
            await ctx.send(msg)
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        dados_cripto = cg.get_coin_by_id(id_cripto)

        if 'market_data' in dados_cripto:
            variacao_24h = dados_cripto['market_data']['price_change_percentage_24h']

            if variacao_24h is not None:
                msg = f"**A variação de {moeda.upper()} nas últimas 24 horas foi de {variacao_24h:.2f}%**" if lang == "pt" else f"**The 24h variation of {moeda.upper()} was {variacao_24h:.2f}%**"
                await ctx.send(msg)
            else:
                msg = "Desculpe, não consegui obter a variação dessa criptomoeda." if lang == "pt" else "Sorry, I couldn't fetch the variation for this cryptocurrency."
                await ctx.send(msg)
        else:
            msg = "Desculpe, não consegui encontrar informações sobre essa criptomoeda." if lang == "pt" else "Sorry, I couldn't find data for this cryptocurrency."
            await ctx.send(msg)

    except Exception as e:
        msg = f"Erro ao buscar a variação: {str(e)}" if lang == "pt" else f"Error fetching variation: {str(e)}"
        await ctx.send(msg)


@bot.tree.command(name="variacao", description="Mostra a variação de uma criptomoeda nas últimas 24 horas.")
async def variacao_slash(interaction: discord.Interaction, coin: str):
    await fetch_variacao_slash(interaction, coin, "pt")


@bot.tree.command(name="variation")
async def variation_slash(interaction: discord.Interaction, coin: str):
    await fetch_variacao_slash(interaction, coin, "en")


async def fetch_variacao_slash(interaction, coin, lang):
    coin = coin.lower()

    try:
        resultado_busca = cg.search(coin)

        if not resultado_busca['coins']:
            msg = "Desculpe, não consegui encontrar essa criptomoeda." if lang == "pt" else "Sorry, I couldn't find this cryptocurrency."
            await interaction.response.send_message(msg)
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        dados_cripto = cg.get_coin_by_id(id_cripto)

        if 'market_data' in dados_cripto:
            variacao_24h = dados_cripto['market_data']['price_change_percentage_24h']

            if variacao_24h is not None:
                msg = f"**A variação de {coin.upper()} nas últimas 24 horas foi de {variacao_24h:.2f}%**" if lang == "pt" else f"**The 24h variation of {coin.upper()} was {variacao_24h:.2f}%**"
                await interaction.response.send_message(msg)
            else:
                msg = "Desculpe, não consegui obter a variação dessa criptomoeda." if lang == "pt" else "Sorry, I couldn't fetch the variation for this cryptocurrency."
                await interaction.response.send_message(msg)
        else:
            msg = "Desculpe, não consegui encontrar informações sobre essa criptomoeda." if lang == "pt" else "Sorry, I couldn't find data for this cryptocurrency."
            await interaction.response.send_message(msg)

    except Exception as e:
        msg = f"Erro ao buscar a variação: {str(e)}" if lang == "pt" else f"Error fetching variation: {str(e)}"
        await interaction.response.send_message(msg)


# Comando para buscar o índice "Fear And Greed" das criptomoedas.
@bot.command(name="fandg")
async def fandg(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        moeda_encontrada = resultado_busca['coins'][0]
        id_cripto = moeda_encontrada['id']

        fandg_url = "https://api.alternative.me/fng/?limit=1"
        response_fandg = requests.get(fandg_url)
        data_fandg = response_fandg.json()

        fandg_valor = data_fandg['data'][0]['value']
        descricao_fandg = data_fandg['data'][0]['value_classification']

        await ctx.send(f"**Fear and Greed {moeda.upper()}: {fandg_valor} ({descricao_fandg})**")

    except Exception as e:
        await ctx.send(f"Erro ao buscar o índice: {str(e)}")


@bot.tree.command(name="fandg", description="Mostra o índice Fear and Greed de uma criptomoeda.")
async def fandg_slash(interaction: discord.Interaction, coin: str):
    coin = coin.lower()

    try:

        resultado_busca = cg.search(coin)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        fandg_url = "https://api.alternative.me/fng/?limit=1"
        response_fandg = requests.get(fandg_url)
        data_fandg = response_fandg.json()

        fandg_valor = data_fandg['data'][0]['value']
        descricao_fandg = data_fandg['data'][0]['value_classification']

        await interaction.response.send_message(f"**Fear and Greed {coin.upper()}: {fandg_valor} ({descricao_fandg})**")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar o índice: {str(e)}")


@bot.command(name="volume")
async def volume(ctx, moeda: str):
    moeda = moeda.lower()

    try:
        resultado_busca = cg.search(moeda)

        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        dados_cripto_brl = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        dados_cripto_usd = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='usd', days=1)

        volume_cripto_brl = dados_cripto_brl['total_volumes'][-1][1]
        volume_cripto_usd = dados_cripto_usd['total_volumes'][-1][1]

        volume_formatado_brl = f"{volume_cripto_brl:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        volume_formatado_usd = f"{volume_cripto_usd:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        await ctx.send(f"**Volume 24h {moeda.upper()}: {volume_formatado_brl} BRL | {volume_formatado_usd} USD**")

    except Exception as e:
        await ctx.send(f"Erro ao buscar o volume: {str(e)}")


@bot.tree.command(name="volume", description="Mostra o volume das negociações de uma criptomoeda em BRL e USD.")
async def volume_slash(interaction: discord.Interaction, coin: str):
    coin = coin.lower()

    try:

        resultado_busca = cg.search(coin)

        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        dados_cripto_brl = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        dados_cripto_usd = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='usd', days=1)

        volume_cripto_brl = dados_cripto_brl['total_volumes'][-1][1]
        volume_cripto_usd = dados_cripto_usd['total_volumes'][-1][1]

        volume_formatado_brl = f"{volume_cripto_brl:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        volume_formatado_usd = f"{volume_cripto_usd:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        await interaction.response.send_message(
            f"**Volume 24h {coin.upper()}: {volume_formatado_brl} BRL | {volume_formatado_usd} USD**")

    except Exception as e:
        await interaction.response.send_message(f"Erro ao buscar o volume: {str(e)}")


""" Sistema do comando "grafico" e versão inglês "chart", 
que imprime o gráfico do preço da criptomoeda selecionada, nas últimas 24h."""


@bot.command(name="grafico")
async def grafico(ctx, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)
        if not resultado_busca['coins']:
            await ctx.send("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        data = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        timestamps = [point[0] for point in data['prices']]
        prices = [point[1] for point in data['prices']]
        horas = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]
        # Cria o gráfico
        plt.figure(figsize=(10, 5))
        plt.plot(horas, prices, label=f"Preço de {moeda.upper()} (BRL)", color="blue", linewidth=2)
        plt.title(f"Gráfico Diário de {moeda.upper()} (BRL)")
        plt.xlabel("Hora")
        plt.ylabel("Preço (USD)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        # Salva o gráfico
        grafico_path = f"{moeda}_daily_chart.png"
        plt.tight_layout()
        plt.savefig(grafico_path)
        plt.close()
        # Envia o gráfico e em seguida remove da pasta.
        await ctx.send(file=discord.File(grafico_path))

        if os.path.exists(grafico_path):
            os.remove(grafico_path)

    except Exception as e:
        await ctx.send(f"Erro ao gerar o gráfico: {str(e)}")


@bot.tree.command(name="grafico", description="Mostra um gráfico diário do preço de uma criptomoeda em BRL.")
async def grafico_slash(interaction: discord.Interaction, moeda: str):
    moeda = moeda.lower()

    try:

        resultado_busca = cg.search(moeda)
        if not resultado_busca['coins']:
            await interaction.response.send_message("Desculpe, não consegui encontrar essa criptomoeda.")
            return

        id_cripto = resultado_busca['coins'][0]['id']

        data = cg.get_coin_market_chart_by_id(id=id_cripto, vs_currency='brl', days=1)
        timestamps = [point[0] for point in data['prices']]
        prices = [point[1] for point in data['prices']]
        horas = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

        plt.figure(figsize=(10, 5))
        plt.plot(horas, prices, label=f"Preço de {moeda.upper()} (BRL)", color="blue", linewidth=2)
        plt.title(f"Gráfico Diário de {moeda.upper()} (BRL)")
        plt.xlabel("Hora")
        plt.ylabel("Preço (BRL)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)

        grafico_path = f"{moeda}_daily_chart.png"
        plt.tight_layout()
        plt.savefig(grafico_path)
        plt.close()

        await interaction.response.send_message(file=discord.File(grafico_path))

        if os.path.exists(grafico_path):
            os.remove(grafico_path)

    except Exception as e:
        await interaction.response.send_message(f"Erro ao gerar o gráfico: {str(e)}")


@bot.command(name="chart")
async def chart(ctx, coin: str):
    coin = coin.lower()

    try:
        result = cg.search(coin)
        if not result['coins']:
            await ctx.send("Sorry, I couldn't find that cryptocurrency.")
            return

        coin_id = result['coins'][0]['id']
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=1)
        timestamps = [point[0] for point in data['prices']]
        prices = [point[1] for point in data['prices']]
        hours = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

        plt.figure(figsize=(10, 5))
        plt.plot(hours, prices, label=f"Price of {coin.upper()} (USD)", color="blue", linewidth=2)
        plt.title(f"Daily Chart of {coin.upper()} (USD)")
        plt.xlabel("Hour")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)

        chart_path = f"{coin}_daily_chart.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        await ctx.send(file=discord.File(chart_path))

        if os.path.exists(chart_path):
            os.remove(chart_path)

    except Exception as e:
        await ctx.send(f"Error generating the chart: {str(e)}")


@bot.tree.command(name="chart")
async def chart_slash(interaction: discord.Interaction, coin: str):
    coin = coin.lower()

    try:
        result = cg.search(coin)
        if not result['coins']:
            await interaction.response.send_message("Sorry, I couldn't find that cryptocurrency.")
            return

        coin_id = result['coins'][0]['id']
        data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=1)
        timestamps = [point[0] for point in data['prices']]
        prices = [point[1] for point in data['prices']]
        hours = [datetime.fromtimestamp(ts / 1000).strftime('%H:%M') for ts in timestamps]

        plt.figure(figsize=(10, 5))
        plt.plot(hours, prices, label=f"Price of {coin.upper()} (USD)", color="blue", linewidth=2)
        plt.title(f"Daily Chart of {coin.upper()} (USD)")
        plt.xlabel("Hour")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)

        chart_path = f"{coin}_daily_chart.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        await interaction.response.send_message(file=discord.File(chart_path))

        if os.path.exists(chart_path):
            os.remove(chart_path)

    except Exception as e:
        await interaction.response.send_message(f"Error generating the chart: {str(e)}")


bot.run(token)
