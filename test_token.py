import discord
import asyncio

async def test_token(token):
    """Testa se um token Discord é válido"""
    try:
        # Cria um cliente simples
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        
        # Tenta fazer login
        await client.login(token)
        print("✅ Token válido!")
        
        # Busca informações do bot
        app_info = await client.application_info()
        print(f"Bot: {app_info.name}")
        print(f"ID: {app_info.id}")
        
        await client.close()
        return True
        
    except discord.errors.LoginFailure:
        print("❌ Token inválido!")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# Para usar (substitua SEU_TOKEN_AQUI pelo token real):
asyncio.run(test_token("SEU_TOKEN_AQUI"))