from datetime import datetime, timedelta

import discord
import kadal
import pytz
from discord.ext import commands
from kadal import MediaNotFound
from tokage import TokageNotFound

MAL_ICON = 'https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png'
AL_ICON = 'https://avatars2.githubusercontent.com/u/18018524?s=280&v=4'


class MyAnimeList:
    def __init__(self, bot):
        self.bot = bot
        self.klient = kadal.Client()
        self.t_client = bot.t_client

    @commands.group()
    async def mal(self, ctx):
        """MyAnimeList commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid command. Use `{ctx.prefix}help mal` for more info")

    async def get_next_weekday(self, startdate, day):
        days = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }
        weekday = days[day]
        d = datetime.strptime(startdate, '%Y-%m-%d')
        t = timedelta((7 + weekday - d.weekday()) % 7)
        return (d + t).strftime('%Y-%m-%d')

    async def get_remaining_time(self, anime):
        if anime.broadcast == "Unknown":
            return "Air time for this anime is unknown."
        day = anime.broadcast.split(" at ")[0][:-1]
        hour = anime.broadcast.split(" at ")[1].split(" ")[0]
        jp_time = datetime.now(pytz.timezone("Japan"))
        air_date = await self.get_next_weekday(jp_time.strftime('%Y-%m-%d'), day)
        time_now = jp_time.replace(tzinfo=None)
        show_airs = datetime.strptime(f'{air_date} - {hour.strip()}', '%Y-%m-%d - %H:%M')
        remaining = show_airs - time_now
        if remaining.days < 0:
            return f'{6} Days {remaining.seconds // 3600} Hours and {(remaining.seconds // 60)%60} Minutes.'
        else:
            return (f'{remaining.days} Days '
                    f'{remaining.seconds // 3600} Hours '
                    f'and {(remaining.seconds // 60)%60} Minutes.')

    @mal.command(name="next")
    async def next_(self, ctx, *, query):
        """Countdown to next episode of an airing anime."""
        async with ctx.typing():
            try:
                try:
                    anime_id = await self.t_client.search_id("anime", query)
                    anime = await self.t_client.get_anime(anime_id)
                except RuntimeError:
                    partial = (await self.t_client.search_anime(query))[0]
                    anime = await partial.request_full()
            except TokageNotFound:
                return await ctx.send(":exclamation: Anime was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        if anime.status == "Finished Airing":
            remaining = f"This anime has finished airing!\n{anime.air_end}"
        else:
            remaining = await self.get_remaining_time(anime)
        embed = discord.Embed(title=anime.title, color=0x0066CC)
        embed.add_field(name="Next Episode", value=remaining)
        embed.set_footer(text='MyAnimeList')
        embed.set_author(name='MyAnimeList', icon_url=MAL_ICON)
        embed.set_thumbnail(url=anime.image)
        await ctx.send(embed=embed)

    @mal.command()
    async def manga(self, ctx, *, query):
        """Searches MAL for a Manga."""
        async with ctx.typing():
            try:
                try:
                    manga_id = await self.t_client.search_id("manga", query)
                    result = await self.t_client.get_manga(manga_id)
                except RuntimeError:
                    partial = (await self.t_client.search_manga(query))[0]
                    result = await partial.request_full()
            except TokageNotFound:
                return await ctx.send(":exclamation: Manga was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        if len(result.synopsis) > 1024:
            result.synopsis = result.synopsis[:1024 - (len(result.link) + 7)] + f"[...]({result.link})"
        em = discord.Embed(title=result.title, colour=0xFF9933)
        em.description = ", ".join(result.genres)
        em.add_field(name="Japanese Title", value=result.japanese_title, inline=True)
        em.add_field(name="Type", value=result.type, inline=True)
        em.add_field(name="Chapters", value=result.chapters, inline=True)
        em.add_field(name="Volumes", value=result.volumes, inline=True)
        em.add_field(name="Score", value=result.score, inline=False)
        em.add_field(name="Status", value=result.status, inline=True)
        em.add_field(name="Published", value=result._publish_time, inline=True)
        em.add_field(name="Synopsis", value=result.synopsis, inline=False)
        em.add_field(name="Link", value=result.link, inline=False)
        em.set_author(name='MyAnimeList', icon_url=MAL_ICON)
        em.set_thumbnail(url=result.image)
        await ctx.send(embed=em)

    @mal.command()
    async def anime(self, ctx, *, query):
        """Searches MAL for an Anime."""
        async with ctx.typing():
            try:
                try:
                    anime_id = await self.t_client.search_id("anime", query)
                    result = await self.t_client.get_anime(anime_id)
                except RuntimeError:
                    partial = (await self.t_client.search_anime(query))[0]
                    result = await partial.request_full()
            except TokageNotFound:
                return await ctx.send(":exclamation: Anime was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        if len(result.synopsis) > 1024:
            result.synopsis = result.synopsis[:1024 - (len(result.link) + 7)] + f"[...]({result.link})"
        em = discord.Embed(title=result.title, colour=0x0066CC)
        em.description = ", ".join(result.genres)
        em.add_field(name="Japanese Title", value=result.japanese_title, inline=True)
        em.add_field(name="Type", value=result.type, inline=True)
        em.add_field(name="Episodes", value=result.episodes, inline=True)
        em.add_field(name="Score", value=result.score, inline=True)
        em.add_field(name="Status", value=result.status, inline=True)
        em.add_field(name="Aired", value=result._air_time, inline=True)
        em.add_field(name="Synopsis", value=result.synopsis, inline=False)
        em.add_field(name="Link", value=result.link, inline=False)
        em.set_author(name='MyAnimeList', icon_url=MAL_ICON)
        em.set_thumbnail(url=result.image)
        await ctx.send(embed=em)

    @mal.command()
    async def char(self, ctx, *, query):
        """Searches MAL for a Character."""
        async with ctx.typing():
            try:
                try:
                    char_id = await self.t_client.search_id("character", query)
                    character = await self.t_client.get_character(char_id)
                except RuntimeError:
                    partial = (await self.t_client.search_character(query))[0]
                    character = await partial.request_full()
            except TokageNotFound:
                return await ctx.send(":exclamation: Character was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        medium = character.animeography if character.animeography else character.mangaography
        jap_va = [va for va in character.voice_actors if va["language"] == "Japanese"][0]
        em = discord.Embed(title="MyAnimeList", colour=0x0066CC)
        if character.image:
            em.set_image(url=character.image)
        em.add_field(name="Name", value=f"[{character.name}]({character.link})")
        series_url = f"[{medium[0]['name']}](https://myanimelist.net{medium[0]['link']})"
        va_url = f"[{jap_va['name']}](https://myanimelist.net{jap_va['link']})"
        em.add_field(name="Series", value=series_url, inline=False)
        em.add_field(name="Voice Actor", value=va_url, inline=False)
        await ctx.send(embed=em)

    @commands.command(name="manga")
    async def al_manga(self, ctx, *, query):
        """Searches Anilist for a Manga."""
        async with ctx.typing():
            try:
                result = await self.klient.search_manga(query, popularity=True)
            except MediaNotFound:
                return await ctx.send(":exclamation: Manga was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        if len(result.description) > 1024:
            result.description = result.description[:1024 - (len(result.site_url) + 7)] + f"[...]({result.site_url})"
        em = discord.Embed(title=result.title['english'], colour=0xFF9933)
        em.description = ", ".join(result.genres)
        em.add_field(name="Japanese Title", value=result.title['native'], inline=True)
        em.add_field(name="Type", value=str(result.format.name).replace("_", " ").capitalize(), inline=True)
        em.add_field(name="Chapters", value=result.chapters or "?", inline=True)
        em.add_field(name="Volumes", value=result.volumes or "?", inline=True)
        em.add_field(name="Score", value=str(result.average_score / 10) + " / 10" if result.average_score else "?",
                     inline=False)
        em.add_field(name="Status", value=str(result.status.name).replace("_", " ").capitalize(), inline=True)
        (year, month, day) = result.start_date.values()
        published = f"{day}/{month}/{year}"
        (year, month, day) = result.end_date.values() if result.end_date['day'] else ('?', '?', '?')
        published += f" - {day}/{month}/{year}"
        em.add_field(name="Published", value=published, inline=True)
        em.add_field(name="Synopsis", value=result.description, inline=False)
        em.add_field(name="Link", value=result.site_url, inline=False)
        em.set_author(name='Anilist', icon_url=AL_ICON)
        em.set_thumbnail(url=result.cover_image)
        await ctx.send(embed=em)

    @commands.command(name="anime")
    async def al_anime(self, ctx, *, query):
        """Searches Anilist for an Anime."""
        async with ctx.typing():
            try:
                result = await self.klient.search_anime(query, popularity=True)
            except MediaNotFound:
                return await ctx.send(":exclamation: Anime was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        if len(result.description) > 1024:
            result.description = result.description[:1024 - (len(result.site_url) + 7)] + f"[...]({result.site_url})"
        em = discord.Embed(title=result.title['english'], colour=0x02a9ff)
        em.description = ", ".join(result.genres)
        em.add_field(name="Japanese Title", value=result.title['native'], inline=True)
        em.add_field(name="Type", value=str(result.format.name).replace("_", " ").capitalize(), inline=True)
        em.add_field(name="Chapters", value=result.episodes or "?", inline=True)
        em.add_field(name="Score", value=str(result.average_score / 10) + " / 10" if result.average_score else "?",
                     inline=False)
        em.add_field(name="Status", value=str(result.status.name).replace("_", " ").capitalize(), inline=True)
        (year, month, day) = result.start_date.values()
        aired = f"{day}/{month}/{year}"
        (year, month, day) = result.end_date.values() if result.end_date['day'] else ('?', '?', '?')
        aired += f" - {day}/{month}/{year}"
        em.add_field(name="Aired", value=aired, inline=True)
        em.add_field(name="Synopsis", value=result.description, inline=False)
        em.add_field(name="Link", value=result.site_url, inline=False)
        em.set_author(name='Anilist', icon_url=AL_ICON)
        em.set_thumbnail(url=result.cover_image)
        await ctx.send(embed=em)

    @commands.command(name="user")
    async def al_user(self, ctx, *, query):
        """Searches Anilist for a User"""
        async with ctx.typing():
            try:
                result = await self.klient.search_user(query)
            except MediaNotFound:
                return await ctx.send(":exclamation: User was not found!")
            except Exception as e:
                return await ctx.send(f":exclamation: An unknown error occured:\n{e}")
        if result.about and len(result.about) > 2000:
            result.about = result.about[:2000 - (len(result.site_url) + 7)] + f"[...]({result.site_url})"
        em = discord.Embed(title=result.name, color=0x02a9ff)
        em.description = result.about
        em.add_field(name="Days Watched", value=round(result.stats.watched_time / 60 / 24, 2))
        em.add_field(name="Chapters Read", value=result.stats.chapters_read)
        em.set_author(name='Anilist', icon_url=AL_ICON)
        em.set_thumbnail(url=result.avatar)
        em.set_image(url=result.banner_image)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(MyAnimeList(bot))
