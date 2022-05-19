package org.vadere.state.attributes.models;

import java.util.Arrays;
import java.util.List;

import org.vadere.annotation.factories.ModelAttributeClass;
import org.vadere.state.attributes.Attributes;


/* Attribute information about SIR Model */
public class AttributesSIRG {

    private int infectionsAtStart = 0;

    private double infectionRate = 0.01;

    private double infectionMaxDistance = 1;

    // TODO : We need to add the recovery rate later.

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

    // TODO : We^ll have recovered/removed getter method later.
}