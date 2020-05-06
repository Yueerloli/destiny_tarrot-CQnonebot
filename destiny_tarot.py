from nonebot import *
import json
import pytz
import asyncio
from random import randint

bot = get_bot()

@on_command('占卜', aliases=('塔罗牌'))
async def tarot(session: CommandSession):
	if session.ctx['message_type'] == 'private':
		if not 'key0' in session.state:
			with open('settings/destiny_tarot/today_record.json') as f:
				record = json.load(f)
			
			user = session.ctx['user_id']
			if str(user) in record.keys():
				if record[str(user)] >= 2:
					session.finish('每天只能占卜2次哦!')
				else :
					record[str(user)] += 1
			else:
				record[str(user)] = 1
			session.state['record'] = record
				
		
		#确定占卜
		if not 'sure' in session.state:
			msg = '注意，每人每天只能占卜2次\n（6:00 a.m.更新）'
			msg += '\n占卜时如果没按提示输入，会被视为放弃机会，一定注意哦'
			msg += '\n确定现在占卜的话,请输入 好'
			the_choice = session.get('key0', prompt=msg)
			if the_choice == '好':
				session.state['sure'] = True
			else:
				session.finish('已取消占卜')
			
		#进行记录
		if not 'dump' in session.state:
			with open('settings/destiny_tarot/today_record.json','w') as f:
				json.dump(session.state['record'],f)
			del session.state['record']
			session.state['dump'] = True
	
		#交代规则
		if not 'key1' in session.state:
			msg = '奈咲酱利用程序尽可能还原了塔罗牌占卜过程'
			msg += '\n包括洗牌、切牌、抽取、翻牌'
			await session.send(msg)
			await asyncio.sleep(1.2)
		if not 'rule' in session.state:
			msg = '我们应用22张大阿卡纳与56张小阿卡纳'
			msg += '\n每张大阿卡纳分正位与逆位，代表不同的意思'
			msg += '\n小阿卡纳每张分别有特定的意思'
			msg += '\n开始时，使用简化的"疑难牌阵"，抽取4张牌(奈咲酱会教你使用哦)'
			msg += '\n抽取完成后，会按顺序翻开'
			msg += '\n输入 好 可以进入下一步哦！'
			the_choice = session.get('key1', prompt=msg)
			if the_choice == '好':
				session.state['rule'] = True
			else:
				session.finish('已退出占卜')
			
		#忠告
		if not 'tip' in session.state:
			msg = '注意了哦，\n塔罗牌功能仅供娱乐，有些重要的事情需要自己做决定'
			msg += '\n请勿过度参考结果或信以为真'
			await session.send(msg)
			session.state['tip'] = True
			await asyncio.sleep(1.5)
			
		#准备
		if not 'ready' in session.state:
			msg = '嗯嗯，那么现在，请再默想一遍困扰主人的问题'
			msg += '如果准备好了的话，对我说 好'
			the_choice = session.get('key2', prompt=msg)
			if the_choice == '好':
				session.state['ready'] = True
			else:
				session.finish('已退出占卜')
				
		#洗牌
		if not 'recards' in session.state:
			await session.send('开始随机打乱卡片')
			all_cards = []
			#加入大阿卡纳
			big_cards_names = ['愚者','魔术师','女教皇','皇帝','女皇','教皇',
				'恋人','战车','力量','隐士','命运之轮','正义','吊人','死神',
				'节制','恶魔','塔','星星','月亮','太阳','审判','世界']
			for big_card_name in big_cards_names:
				direction = randint(1,2)
				if direction == 1:
					direction = '正位'
				else :
					direction = '逆位'
				card_name = big_card_name + ' ' + direction
				all_cards.append(card_name)
			await asyncio.sleep(1)
			#加入小阿卡纳
			small_cards_names = ['SWORDS宝剑','CUP圣杯','WANDS权杖','PENTACES钱币']
			small_cards_types = ['1','2','3','4','5','6','7','8','9','10','侍者','骑士','王后','国王']
			for small_cards_name in small_cards_names:
				for small_cards_type in small_cards_types: 
					card_name = small_cards_name + ' ' + small_cards_type
					all_cards.append(card_name)
			await asyncio.sleep(1)
			#打乱牌库
			cards = []
			while all_cards:
				moved_card = all_cards.pop(randint(0,len(all_cards)-1))
				cards.append(moved_card)
			#完成洗牌
			await session.send('洗牌finish！')
			await asyncio.sleep(0.8)
			
			#切牌
			await session.send('开始切牌!')
			a = randint(25,35) #中间数
			b = randint(5,20) #最小数
			c = randint(40,50) #最大数
			moved_cards = cards[randint(b,a):randint(a,c)]
			await asyncio.sleep(0.8)
			for moved_card in moved_cards:
				cards.remove(moved_card)
				cards.append(moved_card)
			await session.send('切牌也完成了')
			session.state['cards'] = cards
			session.state['recards'] = True
			await asyncio.sleep(0.6)
			
		#抽牌	
		if not 'start_choose' in session.state:
			msg = '接下来是选牌阶段，准备好了的话，请对奈咲酱说 开始选牌'
			the_choice = session.get('key3', prompt=msg)
			if the_choice == '开始选牌':
				session.state['get_cards'] = []
				session.state['start_choose'] = True
			else:
				session.finish('已取消占卜')
		if not 'choose_card' in session.state:
			msg = '牌阵需要4张牌，分别是1,2,3和切牌'
			msg += '\n一共有78张牌，请输入想要选取的牌的序号(正整数)'
			msg += '\n每个数字之间，请输入 和'
			msg += '\n例如： \n1和16和34和78'
			choose_cards = session.get('key4', prompt=msg)
			get_cards = choose_cards.split('和')
			if len(get_cards) == 4:
				try:
					get_cards = map(int,get_cards)
				except ValueError:
					session.finish('序号必须是数字')
				for get_card in get_cards:
					if isinstance(get_card,float):
						session.finish('序号必须是整数')
					elif get_card > 78:
						session.finish('序号不能超过78呢')
					elif get_card < 1:
						session.finish('必须是正数哦!')
					#符合要求
					else:
						get_card_name = session.state['cards'][get_card-1]
						session.state['get_cards'].append(get_card_name)
			else:
				session.finish('格式有误')
			#完成选牌
			await session.send('将这些卡挑出...')
			await asyncio.sleep(1)
			del session.state['cards']
			session.state['start_choose'] = True
			await session.send('选牌也完成了!')
			await asyncio.sleep(0.8)

		
		
		#翻牌
		msg = '下面就要开始翻牌咯，主人!'
		msg += '\n每10秒会翻开一张牌哦'
		await session.send(msg)
		await asyncio.sleep(1.3)
		await session.send('奈咲酱倒数三声，就揭晓第一张牌哦！')
		await asyncio.sleep(1.1)
		await session.send('3')
		await asyncio.sleep(0.8)
		await session.send('2')
		await asyncio.sleep(0.8)
		await session.send('1')
		
		
		#读取
		with open('settings/destiny_tarot/big.json') as f:
			session.state['big'] = json.load(f)
		with open('settings/destiny_tarot/small.json') as f:
			session.state['small'] = json.load(f)
		with open('settings/destiny_tarot/meanings.json') as f:
			session.state['meanings'] = json.load(f)
		#告知结果
		needs = ['1','2','3','切']
		for need in needs:
			seeing = session.state['get_cards'].pop(0)
			
			msg = '准备翻开'
			if need == '切':
				message = '切牌'
			else:
				message = '第' + need +'张牌'
			msg += message
			await asyncio.sleep(0.5)
			await session.send(msg)
			msg = message + ' 结果是:\n'
			msg += seeing
			msg += '\n这张牌'
			msg += session.state['meanings'][need]
			msg += '\n\n这张牌的内涵：\n'
			card_info = seeing.split()
			#小阿卡纳
			if card_info[0] in session.state['small'].keys():
				card_meaning = session.state['small'][card_info[0]][str(card_info[1])]
			#大阿卡纳
			else :
				card_meaning = session.state['big'][card_info[0]][card_info[1]]
			msg+= card_meaning
			await session.send(msg)
			if need == '切':
				del session.state['big']
				del session.state['small']
			await asyncio.sleep(9.2)
		msg = '根据每张牌的意思，主人应该可以解决疑惑了吧'
		msg += '\n但是注意哦，不可以完全将它信以为真，自己也得做出适当判断'
		msg += '\n辣么，祝主人happy every day!'
		await session.send(msg)

	else:
		if session.ctx['group_id'] in bot.config.RECIEVE_FROM_GROUP:
			await session.send('想要用塔罗牌占卜的话，请私聊奈咲酱哦！')
	
	
#每天6点更新记录		
@scheduler.scheduled_job('cron',hour = '6')
async def _():
	new = {}
	with open('settings/destiny_tarot/today_record.json','w') as f:
		json.dump(new,f)
