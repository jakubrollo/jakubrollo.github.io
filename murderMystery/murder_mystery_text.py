from murder_mystery.campaign import MysteryCampaign

def run():
    campaign = MysteryCampaign(total_iterations=3)
    campaign.start()

if __name__ == "__main__":
    run()