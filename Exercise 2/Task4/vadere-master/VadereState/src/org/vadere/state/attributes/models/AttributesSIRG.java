package org.vadere.state.attributes.models;

import org.vadere.state.attributes.Attributes;


/* Attribute information about SIR Model */
public class AttributesSIRG extends Attributes {

    private int infectionsAtStart = 10;

    private double infectionRate = 0.01;

    private double infectionMaxDistance = 1.0;

    private double recoveryRate = 0.005;

    private boolean recoveryEnabled = false;

    /* Getter methods for private attributes */

    public int getInfectionsAtStart() {
        return infectionsAtStart;
    }

    public double getInfectionRate() {
        return infectionRate;
    }

    public double getInfectionMaxDistance() {
        return infectionMaxDistance;
    }

    public double getRecoveryRate() {
        return recoveryRate;
    }

    public boolean getRecoveryEnabled() {
        return recoveryEnabled;
    }
}