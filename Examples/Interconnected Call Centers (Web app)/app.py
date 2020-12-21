from h2o_wave import site, data, ui

def get_objects(n_callcenters):
    ''' Returns a mapping from names to objects representing the cards used in the ui '''
    n_categories = 3
    
    objects = dict()
    
    objects['outcomes'] = ui.plot_card(
        box='1 1 12 5',
        title='Outcomes by Call Center',
        data=data('country callcenter count', n_callcenters*n_categories),
        plot=ui.plot([ui.mark(type='interval', x='=callcenter', y='=count', color='=country', stack='auto', y_min=0)])
    )
                   
    for i in range(n_callcenters):
        col = (i%12)+1
        row = (i//12)*2+6
        objects[f'utilcc{i}'] = ui.tall_gauge_stat_card(
            box=f'{col} {row} 1 2',
            title=f'CC {i:02d} util.',
            value='={{intl perc style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='',
            plot_color='$green',
            progress=0,
            data=dict(perc=0))
    return objects

def initialize(n_callcenters, ymax=1):
    global page
    global cards

    # http://localhost:10101/callcenters
    page = site['/callcenters']

    # delete all objects potentially on the page
    for i in range(16):
        del page[f'utilcc{i}']

    objects = get_objects(n_callcenters)
    cards = dict()
    for name,obj in objects.items():
        cards[name] = page.add(name, obj) 

    #card.data = [["Answered_Local","CC00",36],["Answered_External","CC00",0],["Balked_Call","CC00",41], ["Answered_Local","CC01",39],["Answered_External","CC01",14],["Balked_Call","CC01",0], ["Answered_Local","CC02",64],["Answered_External","CC02",6],["Balked_Call","CC02",0], ["Answered_Local","CC03",75],["Answered_External","CC03",6],["Balked_Call","CC03",0]]
    page.save()

def update(new_bar_data=None, new_util_data=None):
    global page
    global cards

    # data from AL is packed one-layer too deep
    if new_bar_data is not None:
        new_bar_data = [tuple(i) for j in new_bar_data for i in j]
        cards['outcomes'].data = new_bar_data

    if new_util_data is not None:
        for i,val in enumerate(new_util_data):
            key = f'utilcc{i}'
            cards[key].data.perc = val
            cards[key].progress = val
    page.save()

