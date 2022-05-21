package org.vadere.state.attributes;

import org.vadere.state.attributes.Attributes;
import org.vadere.util.factory.attributes.AttributeBaseFactory;

import org.vadere.state.attributes.models.AttributesFloorField;
import org.vadere.state.attributes.models.AttributesOVM;
import org.vadere.state.attributes.models.AttributesReynolds;
import org.vadere.state.attributes.models.AttributesPotentialParticles;
import org.vadere.state.attributes.models.AttributesODEIntegrator;
import org.vadere.state.attributes.models.infection.AttributesProximityExposureModel;
import org.vadere.state.attributes.models.AttributesPotentialOSM;
import org.vadere.state.attributes.models.AttributesPotentialCompact;
import org.vadere.state.attributes.models.AttributesCA;
import org.vadere.state.attributes.models.AttributesQueuingGame;
import org.vadere.state.attributes.models.AttributesTimeCost;
import org.vadere.state.attributes.models.AttributesBHM;
import org.vadere.state.attributes.models.AttributesOSM;
import org.vadere.state.attributes.models.AttributesPotentialRingExperiment;
import org.vadere.state.attributes.models.AttributesBMM;
import org.vadere.state.attributes.models.AttributesGNM;
import org.vadere.state.attributes.models.AttributesSFM;
import org.vadere.state.attributes.models.AttributesParticles;
import org.vadere.state.attributes.models.AttributesSingleTargetStrategy;
import org.vadere.state.attributes.models.AttributesPotentialCompactSoftshell;
import org.vadere.state.attributes.models.AttributesPotentialGNM;
import org.vadere.state.attributes.models.AttributesGFM;
import org.vadere.state.attributes.models.AttributesSTOM;
import org.vadere.state.attributes.models.AttributesSeating;
import org.vadere.state.attributes.models.infection.AttributesThresholdResponseModel;
import org.vadere.state.attributes.models.infection.AttributesAirTransmissionModel;
import org.vadere.state.attributes.models.AttributesCGM;
import org.vadere.state.attributes.models.AttributesPotentialSFM;



public class ModelAttributeFactory extends AttributeBaseFactory<Attributes> {


	private static ModelAttributeFactory instance;

	//good performance threadsafe Singletone. Sync block will only be used once
	public static ModelAttributeFactory instance(){
		if(instance ==  null){
			synchronized (ModelAttributeFactory.class){
				if(instance == null){
					instance = new ModelAttributeFactory();
				}
			}
		}
		return instance;
	}


	private ModelAttributeFactory(){

		addMember(AttributesFloorField.class, this::getAttributesFloorField);
		addMember(AttributesOVM.class, this::getAttributesOVM);
		addMember(AttributesReynolds.class, this::getAttributesReynolds);
		addMember(AttributesPotentialParticles.class, this::getAttributesPotentialParticles);
		addMember(AttributesODEIntegrator.class, this::getAttributesODEIntegrator);
		addMember(AttributesProximityExposureModel.class, this::getAttributesProximityExposureModel);
		addMember(AttributesPotentialOSM.class, this::getAttributesPotentialOSM);
		addMember(AttributesPotentialCompact.class, this::getAttributesPotentialCompact);
		addMember(AttributesCA.class, this::getAttributesCA);
		addMember(AttributesQueuingGame.class, this::getAttributesQueuingGame);
		addMember(AttributesTimeCost.class, this::getAttributesTimeCost);
		addMember(AttributesBHM.class, this::getAttributesBHM);
		addMember(AttributesOSM.class, this::getAttributesOSM);
		addMember(AttributesPotentialRingExperiment.class, this::getAttributesPotentialRingExperiment);
		addMember(AttributesBMM.class, this::getAttributesBMM);
		addMember(AttributesGNM.class, this::getAttributesGNM);
		addMember(AttributesSFM.class, this::getAttributesSFM);
		addMember(AttributesParticles.class, this::getAttributesParticles);
		addMember(AttributesSingleTargetStrategy.class, this::getAttributesSingleTargetStrategy);
		addMember(AttributesPotentialCompactSoftshell.class, this::getAttributesPotentialCompactSoftshell);
		addMember(AttributesPotentialGNM.class, this::getAttributesPotentialGNM);
		addMember(AttributesGFM.class, this::getAttributesGFM);
		addMember(AttributesSTOM.class, this::getAttributesSTOM);
		addMember(AttributesSeating.class, this::getAttributesSeating);
		addMember(AttributesThresholdResponseModel.class, this::getAttributesThresholdResponseModel);
		addMember(AttributesAirTransmissionModel.class, this::getAttributesAirTransmissionModel);
		addMember(AttributesCGM.class, this::getAttributesCGM);
		addMember(AttributesPotentialSFM.class, this::getAttributesPotentialSFM);
	}


	// Getters
	public AttributesFloorField getAttributesFloorField(){
		return new AttributesFloorField();
	}

	public AttributesOVM getAttributesOVM(){
		return new AttributesOVM();
	}

	public AttributesReynolds getAttributesReynolds(){
		return new AttributesReynolds();
	}

	public AttributesPotentialParticles getAttributesPotentialParticles(){
		return new AttributesPotentialParticles();
	}

	public AttributesODEIntegrator getAttributesODEIntegrator(){
		return new AttributesODEIntegrator();
	}

	public AttributesProximityExposureModel getAttributesProximityExposureModel(){
		return new AttributesProximityExposureModel();
	}

	public AttributesPotentialOSM getAttributesPotentialOSM(){
		return new AttributesPotentialOSM();
	}

	public AttributesPotentialCompact getAttributesPotentialCompact(){
		return new AttributesPotentialCompact();
	}

	public AttributesCA getAttributesCA(){
		return new AttributesCA();
	}

	public AttributesQueuingGame getAttributesQueuingGame(){
		return new AttributesQueuingGame();
	}

	public AttributesTimeCost getAttributesTimeCost(){
		return new AttributesTimeCost();
	}

	public AttributesBHM getAttributesBHM(){
		return new AttributesBHM();
	}

	public AttributesOSM getAttributesOSM(){
		return new AttributesOSM();
	}

	public AttributesPotentialRingExperiment getAttributesPotentialRingExperiment(){
		return new AttributesPotentialRingExperiment();
	}

	public AttributesBMM getAttributesBMM(){
		return new AttributesBMM();
	}

	public AttributesGNM getAttributesGNM(){
		return new AttributesGNM();
	}

	public AttributesSFM getAttributesSFM(){
		return new AttributesSFM();
	}

	public AttributesParticles getAttributesParticles(){
		return new AttributesParticles();
	}

	public AttributesSingleTargetStrategy getAttributesSingleTargetStrategy(){
		return new AttributesSingleTargetStrategy();
	}

	public AttributesPotentialCompactSoftshell getAttributesPotentialCompactSoftshell(){
		return new AttributesPotentialCompactSoftshell();
	}

	public AttributesPotentialGNM getAttributesPotentialGNM(){
		return new AttributesPotentialGNM();
	}

	public AttributesGFM getAttributesGFM(){
		return new AttributesGFM();
	}

	public AttributesSTOM getAttributesSTOM(){
		return new AttributesSTOM();
	}

	public AttributesSeating getAttributesSeating(){
		return new AttributesSeating();
	}

	public AttributesThresholdResponseModel getAttributesThresholdResponseModel(){
		return new AttributesThresholdResponseModel();
	}

	public AttributesAirTransmissionModel getAttributesAirTransmissionModel(){
		return new AttributesAirTransmissionModel();
	}

	public AttributesCGM getAttributesCGM(){
		return new AttributesCGM();
	}

	public AttributesPotentialSFM getAttributesPotentialSFM(){
		return new AttributesPotentialSFM();
	}


}
