package org.vadere.state.scenario.distribution.registry;

import java.util.HashMap;
import java.util.Set;

import org.reflections.Reflections;
import org.vadere.state.scenario.distribution.VadereDistribution;

/**
 * @author Aleksandar Ivanov(ivanov0@hm.edu)
 */
public class DistributionRegistry {

	private static HashMap<String, RegisteredDistribution> REGISTRY = findDistributions();

	public static RegisteredDistribution get(String name) throws Exception {
		if (!REGISTRY.containsKey(name)) {
			throw new Exception(
			        "There is no distribution with name " + name + ". Possible options are " + getRegisteredNames());
		}

		return REGISTRY.get(name);
	}

	public static Set<String> getRegisteredNames() {
		return REGISTRY.keySet();
	}

	private static HashMap<String, RegisteredDistribution> findDistributions() {
		Reflections reflections = new Reflections("org.vadere.state.scenario.distribution.impl");
		Set<Class<?>> distributions = reflections.getTypesAnnotatedWith(RegisterDistribution.class);

		HashMap<String, RegisteredDistribution> registry = new HashMap<String, RegisteredDistribution>();

		distributions.forEach(clazz -> {
			RegisterDistribution annotation = clazz.getAnnotation(RegisterDistribution.class);

			if (VadereDistribution.class.isAssignableFrom(clazz)) {
				@SuppressWarnings("unchecked") // safe to cast because clazz extends VadereDistribution
				Class<? extends VadereDistribution<?>> vadereDistributionclazz = (Class<? extends VadereDistribution<?>>) clazz;
				RegisteredDistribution a = new RegisteredDistribution(annotation.parameter(), vadereDistributionclazz);
				registry.put(annotation.name(), a);
			}

			else {
				System.out.println(DistributionRegistry.class.getName() + ": " + clazz
				        + "will be skipped because it does not extend VadereDistribution");
			}

		});

		return registry;
	}

}
