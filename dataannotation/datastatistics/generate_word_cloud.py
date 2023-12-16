import matplotlib.pyplot as plt
from wordcloud import WordCloud


# List of datasets as a single string


def generate_word_cloud(
		datasets: str,
		title: str,
		width: int = 1000,
		height: int = 500,
		background_color: str = 'white'
):
	wordcloud = WordCloud(width=1000, height=500, background_color='white').generate(datasets)
	
	plt.figure(figsize=(15, 10))
	plt.imshow(wordcloud, interpolation='bilinear')
	plt.axis('off')
	
	plt.savefig("./presentation/word_clouds/" + title + ".png")
	plt.show()


if __name__ == '__main__':
	machine_learning_datasets = """
	MNIST CIFAR-10 CIFAR-100 ImageNet COCO ADE20K VisualQA LFW CelebA SVHN VOC PASCAL
	Caltech101 UCF101 Kinetics RAVDESS WIDER FACE YouTube-8M Google LandmarkRecognition
	Cityscapes KITTI NYU Depth V2 SUN Database Fashion MNIST Oxford Pets
	Oxford Flowers Aerial Image DIV2K BigGAN DAVIS iMaterialist DeepFashion2 EmoReact
	CUB-200-2011 FER2013 MS MARCO Humpback Whale Open Images Tiny ImageNet Places365
	EuroSAT SIFT1M Flickr30k MS COCO LSUN Food-101 Stanford Dogs PlantCLEF Traffic Sign
	Waymo Human3.6M Assembly101 EPICKITCHENS Ego4D Breakfast Charades ActivityNet Inria YouCook2 CrossTask
	ProceL COIN 50Salads EGTEA EgoProceL EgoTV
	"""
	
	ego_centric_vision_datasets = """
	Ego4D EPICKitchens Assembly101 EgoProceL EGTEA EgoHands ADL UTE EgoGesture FPSI Disney EgoCap FPHA
	CharadesEgo WHO EYEDIAP MECCANO EGOCH EgoMon EgoVox EgoYouTube YouCook2 BAD HUJI EgoSeg
	PAVIS EgoTopo EgoRoutine NTURGBD120
	"""
	
	selected_recipes = """
	Coffee Pinwheels MugCake MicrowaveEggSandwich DressedUpMeatballs MicrowaveMugPizza Ramen BreakfastBurritos
	SpicedHotChocolate MicrowaveFrenchToast TomatoMozzarellaSalad ButterCornCup TomatoChutney ScrambledEggs
	CucumberRaita Zoodles SautedMushrooms BlenderBananaPancakes HerbOmeletFriedTomatoes BroccoliStirFry PanFriedTofu
	CheesePimiento SpicyTunaAvocadoWraps CapreseBruschetta
	"""
	
	# generate_word_cloud(machine_learning_datasets, "MachineLearningDatasets")
	# generate_word_cloud(ego_centric_vision_datasets, "Ego-CentricVisionDatasets")
	generate_word_cloud(selected_recipes, "SelectedRecipeDatasets")
